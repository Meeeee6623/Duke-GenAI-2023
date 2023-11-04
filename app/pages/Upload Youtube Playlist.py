import streamlit as st

from app.utils.youtube import get_playlist_info, get_videos
from app.utils.openai_connector import call_llm

st.set_page_config(page_title="Youtube Playlist Manual Uploader", page_icon=":notes:")

st.title('Youtube Playlist Manual Uploader')

playlist_url = st.text_input("Playlist URL", "")
if st.button("Get Playlist Info"):
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
    st.success("Done! Description:")
    # get playlist description and make user editable
    playlist_description = st.text_area("Playlist Description", synthetic_description)

    # chunk and upload videos
