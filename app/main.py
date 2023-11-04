import openai
import streamlit as st
import os
import requests


from app.utils.queries import get_top_k_playlists, search_playlist
from app.utils.youtube import get_yt_playlists
from app.utils.upload_videos import upload_videos
from app.utils.openai_connector import call_llm

openai.api_key = os.getenv("OPENAI_APIKEY")

# Define the YouTube video IDs
playlist_ids = ["video1", "video2", "video3"]

# Create a list to store the selected videos
selected_playlists = []


# Save the selected videos as a variable
st.session_state["selected_playlists"] = selected_playlists

st.title("💬  LOLA: Learn Online Like Actually")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you? I can learn from Youtube and teach you just about anything!",
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
    system_prompt = f"""You’re the chat module for the Learn Anything Tutor. Your job is to have a super natural, conversational chat with the student and identify what they want to learn about. Don't ask multiple questions at once, take it turn by turn like a human would talk to another human. Require that they give you very specific details about what they want to work on, detailing their experience level and their purpose in learning that material. Also work to understand how they learn best: what kind of teaching style do they want from you as the AI tutor (this mostly defines the tone of the text you write, so don't suggest crazy things like interactive diagramming). Don't waste my time diving infinitely into what I want to learn, you'll know when you know what to search for. 

Once you’ve identified what the student wants to learn about and why (giving you the right information to generate a tutor bot for them), you’ll output a few pieces of information in a very specific way, to initialize the tutor bot. You’ll decide when you’re ready to do this and make sure you include the [S], [T] and [B] labels.

Here’s the format you’ll output in once you’ve had a conversation really understanding the student and their purpose for building the tutor. It should be labeled with [S], [T],[T],[T], and [B].

Example final output from our conversation:
[S]
Making chocolate chips cookies from scratch, including collecting the right ingredients, cooking them right and preparing them for a picnic. The user is looking to get ready for an upcoming picnic with friends, and is learning to make chocolate chip cookies for the first time.

[T]  
"Ingredients for chocolate chip cookies"
[T] 
"Cooking chocolate chip cookies"
[T] 
"How to prepare cookies for a picnic."
[B] 
You'll be a cookie-making tutor who breaks things down step by steps, checks in on the user at every step to make sure they understand, and follows up on questions, calls back ideas and remembers the conversation history. 
----
Make sure you end up putting out those letters so I can parse them out and initialize the chatbot. The topics sections of your output are going to be used to search Youtube, so make sure they are exactly what I'd need to search for to find the information. Essentially, you use the T labeled sections to make Youtube searches for me.  Good Youtube searches are super precise.

If, for example, I want to learn how to tame monkeys, I might want a topic "How to tame a monkey" or "How to have a pet chimpanzee" if that's what I specified. These topics are important and you should take care to do them precisely.

Ok I'm the student, let's begin!

"""

    # Get the response from the LLM call function
    response_text, conversation, total_tokens, response = call_llm(
        user_query=query, conversation=None, system_prompt=system_prompt
    )

    group_dict = parse(response_text, ["[S]", "[T]", "[B]"])
    # testing
    st.write(group_dict)
    if group_dict is None:
        # if the response has [D] - meaning we want to ask the user another question:
        # Update the session state messages with the assistant's response
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

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
            else:
                # we need to search YT for a playlist and let a user choose stuff
                youtube_query = group_dict.get("[T]")
                youtube_query.append(group_dict.get("[S]"))
                playlist_ids = get_yt_playlists(youtube_query, k=3)
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

        # Get the response from the LLM call function
        response_text, conversation, total_tokens, response = call_llm(
            user_query=query, conversation=None, system_prompt=system_prompt
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

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
# upload_videos(playlist_id)

# search through playlists for topic
# search_playlist(playlist_id, query, k)
