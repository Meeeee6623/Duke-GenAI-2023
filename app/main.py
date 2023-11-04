# First
import openai
import streamlit as st
import os

openai.api_key = os.getenv("OPENAI_APIKEY")

import requests

# Define the YouTube video IDs
video_ids = ["video1", "video2", "video3"]

# Create a list to store the selected videos
selected_videos = []

# Display the videos and checkboxes in the sidebar
with st.sidebar:
    st.title("Select Videos")
    for video_id in video_ids:
        # Fetch the YouTube video thumbnail
        response = requests.get(f"https://img.youtube.com/vi/{video_id}/default.jpg")
        thumbnail_url = response.url

        # Display the thumbnail and checkbox
        thumbnail = f'<img src="{thumbnail_url}" alt="Thumbnail" width="200">'
        checkbox_label = f"{thumbnail} Video {video_id}"
        st.write(checkbox_label)
        checkbox = st.checkbox(checkbox_label)
        if checkbox:
            selected_videos.append(video_id)

# Save the selected videos as a variable
st.session_state["selected_videos"] = selected_videos

st.title("💬 LOLA: Learn Online Like Actually")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you? I can learn and teach you anything!",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # main logic here
    # need checks if we have data and etc

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=st.session_state.messages
    )
    msg = response.choices[0].message
    st.session_state.messages.append(msg)
    st.chat_message("assistant").write(msg.content)
