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
            response = requests.get(
                f"https://img.youtube.com/vi/{playlist_id}/default.jpg"
            )
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


if query := st.chat_input():
    # main logic here
    # prompt 1

    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)

    # prompt number 1
    system_prompt = "I am an AI trained to talk to you! How can I assist you today?"

    # Get the response from the LLM call function
    response_text, conversation, total_tokens, response = call_llm(
        user_query=query, conversation=None, system_prompt=system_prompt
    )
    
    group_dict = parse(response_text, ["[S]","[T]","[B]"])
    
    
    if group_dict is None:
        # if the response has [D] - meaning we want to ask the user another question:
        # Update the session state messages with the assistant's response
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Write the assistant response to the chat
        st.chat_message("assistant").write(response_text)

        # else start finding out topics and descrition:
        # topics = list of topics
    else:
        ################################################################
        for topic in st.session_state.topics:
            # do the loop for each topic
            # prompt 3 - for each topic compare it to the weaviate playlist context
            # if topic matches a playlist -> playlist_id = match
            # if doesn't match -> search yt, then prompt user for playlist

            if playlist_id:
                # we have the playlist with info
                topic_context_dict = search_playlist(playlist_id, query, k=3)

                # Add relevant topic info to the prompt
                # use like: You learned {context} about {topic} or something
                system_prompt = f""" {topic_context_dict} I am an AI trained to talk to you! How can I assist you today?"""

        # Get the response from the LLM call function
        response_text, conversation, total_tokens, response = call_llm(
            user_query=query, conversation=None, system_prompt=system_prompt
        )
        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Write the assistant response to the chat
        st.chat_message("assistant").write(response_text)


# function names

# parsing function
import re

def parse(text, groups):
    group_dict = {}
    for group in groups:
        # The pattern is designed to capture text for each group letter
        # It handles optional newlines and spaces around the brackets.
        pattern = r"\[" + re.escape(group) + r"\](.*?)(?=\[\w\]|$)"
        matches = re.findall(pattern, text, re.DOTALL)
        # Removing leading/trailing whitespaces for each match
        group_dict[group] = [match.strip() for match in matches]
    return group_dict


# data is a dictionary that has like [s] : short descriptions, [T] : topic etc ...], [B] : behavior

# data = parse_response(response)

# weaviate query for top k playlists:
# get_top_k_playlists(query, k)

# youtube search for top k playlists:
# get_yt_playlists(query, k)

# chunk and upload videos from playlist
# upload_playlist_videos(playlist_id)

# search through playlists for topic
# search_playlist(playlist_id, query, k)
