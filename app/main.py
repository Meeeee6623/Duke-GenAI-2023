# First
import openai
import streamlit as st
import os
import requests

openai.api_key = os.getenv("OPENAI_APIKEY")

# Define the YouTube video IDs
playlist_ids = ["video1", "video2", "video3"]

# Create a list to store the selected videos
selected_playlists = []

# Display the videos and checkboxes in the sidebar
if playlist_ids is not None:
    with st.sidebar:
        st.title("Select Videos")
        for playlist_id in playlist_ids:
            # Fetch the YouTube video thumbnail
            response = requests.get(f"https://img.youtube.com/vi/{playlist_id}/default.jpg")
            thumbnail_url = response.url

            # Display the thumbnail and checkbox
            st.image(thumbnail_url, width=250)
            checkbox_label = f"Select {playlist_id}"
       
            checkbox = st.checkbox(checkbox_label)
            if checkbox:
                selected_playlists.append(playlist_id)

# Save the selected videos as a variable
st.session_state["selected_playlists"] = selected_playlists

st.title("💬  LOLA: Learn Online Like Actually")
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

# function names
# weaviate query for top k playlists:
# get_top_k_playlists(query, k)

# youtube search for top k playlists:
# get_yt_playlists(query, k)

# chunk and upload videos from playlist
# upload_playlist_videos(playlist_id)

# search through playlists for topic
# search_playlist(playlist_id, query, k)
