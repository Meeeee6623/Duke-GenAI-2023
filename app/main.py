import streamlit as st
import os
import requests
import threading


from app.utils.queries import get_top_k_playlists, search_playlist
from app.utils.youtube import get_yt_playlists, get_yt_playlist_texts
from app.utils.upload_videos import upload_videos
from app.utils.openai_connector import call_llm

import dotenv



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


# Initialize the YouTube API client
youtube = build('youtube', 'v3', developerKey=os.load("YT_API_KEY"))

def fetch_first_video_thumbnail(playlist_id):
    # Fetch the first video in the playlist to get its thumbnail
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=playlist_id,
        part="snippet",
        maxResults=1
    )
    playlistitems_list_response = playlistitems_list_request.execute()
    
    # Get the video ID of the first video
    first_video_id = playlistitems_list_response['items'][0]['snippet']['resourceId']['videoId']
    thumbnail_url = f"https://img.youtube.com/vi/{first_video_id}/default.jpg"
    
    return thumbnail_url


# Create a list to store the selected videos
selected_playlists = []
topic_context_dict = {}

#Prompt to start convo
make_searches= f"""You’re the chat module for the Learn Anything Tutor. Your job is to have a super natural, conversational chat with the student and identify what they want to learn about. Don't ask multiple questions at once, take it turn by turn like a human would talk to another human. Require that they give you very specific details about what they want to work on, detailing their experience level and their purpose in learning that material. Also work to understand how they learn best: what kind of teaching style do they want from you as the AI tutor (this mostly defines the tone of the text you write, so don't suggest crazy things like interactive diagramming). Don't waste my time diving infinitely into what I want to learn, you'll know when you know what to search for. 

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


st.title("💬  LOLA: Learn Online Like Actually")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": make_searches,
        }
    ]
    #Display the chat messages that exist
for msg in st.session_state.messages:
    if(msg['role'] == 'system'):
        continue
    else:
     st.chat_message(msg["role"]).write(msg["content"])

# As long as query not empty make it input
if query := st.chat_input():
    #Run the conversation with the user
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
        user_query=query, conversation=st.session_state.messages, system_prompt=system_prompt
    )
    #st.write(response_text)

    group_dict = parse(response_text, ["S", "T", "B"])
    # testing
    st.write(group_dict["S"])
    if group_dict["S"] == []: #todo check this
        # Update the session state messages with the assistant's response
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

        # Write the assistant response to the chat
        st.chat_message("assistant").write(response_text)

        # else start finding out topics and descrition:
        # topics = list of topics
    else:
        st.chat_message("assistant").write("Let me see if I already learned this topic...")
        st.session_state.topics = group_dict["T"] 
        ################################################################
        for topic in st.session_state.topics:
            # do the loop for each topic
            # prompt 3 - for each topic compare it to the weaviate playlist context
            # if topic matches a playlist -> playlist_id = match
            # if doesn't match -> search yt, then prompt user for playlist
             # prompt number 3
            playlist_ids = get_yt_playlists(query, k=3)
            system_prompt = f"""You are provided with a list of playlists, each with a unique identifier and a description. Your task is to determine if any of these playlists contain information that matches a specific topic.
Given topic: Mudskipper migration patterns
Playlists:
ID: PLOrDN6HaH3OTqZDHNvn2N43FjZuKVqDHz, Description: 'Exploring the depths of marine biology and the behaviors of intertidal species.'
ID: PLOrDN6HaH3OTqZDHN827223FjZ3o4yKVqDHz, Description: 'The fascinating world of amphibious creatures and their survival strategies.'
ID: IBWIBFEWIjd3245782u4yi23jZuKVqDHz, Description: 'Understanding the ecosystem dynamics and animal migrations within mangrove forests.'
Review each playlist description and identify if it closely matches the given topic. If a playlist's description matches the topic, output the playlist's ID next to [P]. If none of the playlist descriptions match the topic, simply output 'no'.

What is your output?"""

            # Get the response from the LLM call function
            response_text, conversation, total_tokens, response = call_llm(
                user_query=query, conversation=None, system_prompt=system_prompt
            )
            #todo how many playlists are we getting?
            playlist_id = parse(response_text, ["P"])

            if playlist_id:
                # we have the playlist with info
                topic_context_dict.append(search_playlist(playlist_id, query, k=3))

            else:
                # we need to search YT for a playlist and let a user choose stuff
                youtube_query = st.session_state.topics
                #youtube_query.append(group_dict["S"])
                playlist_data = get_yt_playlists(youtube_query, k=3)
                playlist_ids = playlist_data["playlist_id"]
                # Display the videos and checkboxes in the sidebar
                if playlist_ids is not None:
                    with st.sidebar:
                        st.title("Select Videos - each one takes a minute")
                        for playlist in playlist_data:
                             # Fetch the YouTube video thumbnail
                            thumbnail_url = fetch_first_video_thumbnail(playlist["playlist_id"])
            

                            # Display the thumbnail and checkbox
                            st.image(thumbnail_url, width=250)
                            checkbox_label = f"Select {playlist_id}"

                            checkbox = st.checkbox(checkbox_label)
                            if checkbox:
                                selected_playlists.append(playlist_id)
                    for playlist_id in selected_playlists:
                        # Start a new thread for each upload_videos call
                        st.write(f"loading in video data from the playlist {playlist_id}")
                        threading.Thread(
                            target=upload_videos, args=(playlist_id,)
                        ).start()

        # Get the response from the LLM call function
        response_text, conversation, total_tokens, response = call_llm(
            user_query=query, conversation=st.session_state.messages, system_prompt=system_prompt
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

        # Write the assistant response to the chat
        st.chat_message("assistant").write(response_text)


# function names
    
# data is a dictionary that has like [s] : short descriptions, [T] : topic etc ...], [B] : behavior
# data = parse_response(response)

# weaviate query for top k playlists:
#get_top_k_playlists(query, k)

# youtube search for top k playlists:
# get_yt_playlists(query, k)

# chunk and upload videos from playlist
# upload_videos(playlist_id)

# search through playlists for topic
# search_playlist(playlist_id, query, k)
