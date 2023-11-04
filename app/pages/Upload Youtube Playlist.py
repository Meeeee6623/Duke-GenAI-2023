import streamlit as st

from app.utils.youtube import get_playlist_info, get_videos
from app.utils.openai_connector import get_video_topics

st.set_page_config(page_title="Youtube Playlist Manual Uploader", page_icon=":notes:")

st.title('Youtube Playlist Manual Uploader')

playlist_url = st.text_input("Playlist URL", "")
playlist_id = playlist_url.split("list=")[1]

# get playlist title with youtube API
playlist_info = get_playlist_info(playlist_id)
st.write(playlist_info)
# get playlist items with youtube API
videos = get_videos(playlist_id)
st.write(videos)
# get playlist description and make user editable
yt_playlist_description = playlist_info['description']
playlist_description = st.text_area("Playlist Description", yt_playlist_description)

# chunk and upload videos
