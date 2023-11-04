import subprocess

import streamlit as st

from app.utils.youtube import get_playlist_info, get_videos
from app.utils.openai_connector import call_llm
from app.utils.data_changes import create_playlist
from app.utils.upload_videos import upload_videos

st.set_page_config(page_title="Youtube Playlist Manual Uploader", page_icon=":notes:")

st.title('Youtube Playlist Manual Uploader')

playlist_url = st.text_input("Playlist URL", "")

if st.toggle("Get Playlist Info"):
    playlist_id = playlist_url.split("list=")[1]

    # get playlist title with youtube API
    playlist_info = get_playlist_info(playlist_id)
    st.write(playlist_info)
    # get playlist items with youtube API
    videos = get_videos(playlist_id)
    st.write(videos)
    # make playlist description from all video titles + openai call
    st.write("Making a synthetic description from the video titles (using OpenAI call)")
    titles = [video['title'] for video in videos]
    synthetic_description = call_llm(f"""
    Write a playlist description for a playlist titled "{playlist_info['title']}".
    The playlist contains the following videos:
    {titles}
    Make sure the description is short but detailed, Roughly 1-2 sentences.
    
    For example, a playlist named "How to make a cake" with the following videos:
    "1. What is a cake"
    "2. How to make a cake"
    "3. How to bake a cake"
    "4. Different types of cakes"
    should have a description like:
    "Information about cakes: What cakes are, how to make cakes, how to bake cakes, and different types of cakes."
    
    Keep everything succinct, and prefer to add "buzz words" or "key words" over long sentence descriptions.
    Avoid starting with "This playlist provides..." or "This playlist is about...". Just get right into the content
    """)
    st.success("Done making description!")
    # get playlist description and make user editable
    st.write(f"Title: {playlist_info['title']}")
    playlist_description = st.text_area("Playlist Description (editable)", synthetic_description[0])
    if st.toggle("Upload Playlist"):
        st.write("Uploading playlist...")
        # upload playlist to weaviate
        result = create_playlist(playlist_id, playlist_info['title'], playlist_description)
        if "error" in result:
            st.write("Playlist already exists!")
        else:
            st.success("Playlist uploaded successfully!")
        st.balloons()
        if st.toggle("Chunk and Upload Videos"):
            st.write("Chunking and uploading videos...")
            # chunk videos and upload to weaviate
            command = ["python", '-u', 'app/utils/upload_videos.py', f'{playlist_id}']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            while process.poll() is None:
                line = process.stdout.readline()
                if not line:
                    continue
                st.write(line.strip())
            st.success("Videos uploaded successfully!")
            st.balloons()
