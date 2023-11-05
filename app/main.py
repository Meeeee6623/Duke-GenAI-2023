import streamlit as st
import os
import requests
import threading

from app.utils.queries import get_top_k_playlists, search_playlist, get_top_k_topics
from app.utils.youtube import get_yt_playlists
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


make_searches = f"""You’re the chat module for the Learn Anything Tutor. Your job is to have a super natural, conversational chat with the student and identify what they want to learn about. Don't ask multiple questions at once, take it turn by turn like a human would talk to another human. Require that they give you very specific details about what they want to work on, detailing their experience level and their purpose in learning that material. Also work to understand how they learn best: what kind of teaching style do they want from you as the AI tutor (this mostly defines the tone of the text you write, so don't suggest crazy things like interactive diagramming). Limit your follow up questions to only 3 follow up questions, and be concise.

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
    """  # Prompt horrible f

st.title("💬  LOLA: Learn Online Like Actually")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": make_searches,
        }
    ]

# Display the chat messages that exist

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    else:
        st.chat_message(msg["role"]).write(msg["content"])

# Create a list to store the selected videos
if "selected_playlists" not in st.session_state:
    st.session_state["selected_playlists"] = []
if "topic_context_info" not in st.session_state:
    st.session_state["topic_context_info"] = []
if "end" not in st.session_state:
    st.session_state["end"] = False
if "topics_covered" not in st.session_state:
    st.session_state.topics_covered = {}

if "stage" not in st.session_state:
    st.session_state["stage"] = "chat"
if st.session_state["stage"] == "chat":
    # ALL RETRIEVAL
    # Prompt to start convo

# As long as query not empty make it input
if query := st.chat_input():
    # Run the conversation with the user
    st.session_state.messages.append({"role": "user", "content": query})
    st.chat_message("user").write(query)

        # Get the response from the LLM call function
        response_text, conversation, total_tokens, response = call_llm(
            user_query=query,
            conversation=st.session_state.messages,  # Dropped system prompt here --> Bug prone?
        )
        # st.write(response_text)

        group_dict = parse(response_text, ["S", "T", "B"])
        print(group_dict)
        group_dict["S"] = ["BMW Cars and engines from a beginner's perspective"]
        group_dict["T"] = ["bmw car models", "bmw car engines"]
        st.write(group_dict)  # Just another testing
        if not group_dict["S"]:  # maybe check T here too?
            # Update the session state messages with the assistant's response
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )

            # Write the assistant response to the chat
            # st.chat_message("assistant").write(response_text)

            # else start finding out topics and description:
            # topics = list of topics
        else:
            st.chat_message("assistant").write("Preparing to teach...")
            st.session_state.topics = group_dict["T"]
            ################################################################
            st.session_state["stage"] = "playlist"
if st.session_state["stage"] == "playlist": 
        for topic in st.session_state.topics:
            if topic in st.session_state.topics_covered.keys():
                continue
            # ### this part is saying  that we have the playlist
            # do the loop for each topic
            # prompt 3 - for each topic compare it to the weaviate playlist context
            # if topic matches a playlist -> playlist_id = match
            # if doesn't match -> search yt, then prompt user for playlist
            # prompt number 3
            st.session_state.current_topic = topic
            st.session_state["top_k_playlist"] = get_top_k_topics(topic, k=3, threshold=0.5)
            print(f"top k playlists: {st.session_state['top_k_playlist']}")
            if len(st.session_state["top_k_playlist"]) == 0:
                st.write("No playlists found")
                continue
            topic_text = ""
            for top_topic in st.session_state["top_k_playlist"]:
                topic_text += f"ID: {top_topic['videoID']}, Title: {top_topic['topic']}, Text: {top_topic['text']} \n"
            playlist_match = f""" You are provided with a list of pieces of information, each with a unique identifier. 
            Your task is to determine if any of these pieces contain information that will exactly 
            answer questions about a specific topic. Be extremely specific. Given topic: {topic}\n
                    Information:\n
                        {topic_text} Review each playlist description and identify if it closely matches the given 
                        topic. If a playlist's description matches the topic, output each playlist's ID after a [P]. 
                        If none of the playlist descriptions match the topic, simply output 'no'. Be very specific. 
                        For example, Topic: "types of cookies" Information: "baking cookies" would recieve the output 
                        No, as it is not specific enough\n Again, do not hesitate to reject something if the details 
                        do not match, even if they are about the same subject. What is your output?"""

            # Get the response from the LLM call function
            response_text, conversation, total_tokens, response = call_llm(
                user_query=playlist_match, conversation=None
            )
            print(f"Playlist Match Prompt: {playlist_match}")
            print(f"Response Text: {response_text}")
            # todo how many playlists are we getting?
            playlist_id = parse(response_text, ["P"])["P"]
            st.write(f"playlist id: {playlist_id}")

            if playlist_id:
                for p_id in playlist_id:
                    st.session_state.topics_covered[topic] = p_id
                    st.write(f"topics covered: {st.session_state.topics_covered}")
            else:
                st.write("No playlists matched")
                st.session_state["stage"] = "ask_for_playlist"
                break
if st.session_state["stage"] == "ask_for_playlist":
    # we dont have a playlist for the user - reload here
    # click submit -> save playlist to topics covered
    # we need to search YT for a playlist and let a user choose stuff
    topic = st.session_state.current_topic
    # st.write(f"topic: {topic}")
    playlist_data = get_yt_playlists(topic, k=3)

    # send a message with each playlist title and a number next to it
    # prompt user to select a playlist
    playlists = ""
    for i, playlist in enumerate(playlist_data):
        playlists += f"{i}: {playlist['title']}\n"
    st.chat_message("assistant").write(
        f"""Which playlist would you like me to learn from? (enter a number): \n {playlists}""")
    st.session_state.messages.append(
        {"role": "assistant", "content": f"Which playlist would you like to select? (enter a number): \n{playlists}"})
    # wait for user input to continue
    try:
        playlist_number = int(query)
    except Exception as e:
        st.stop()  # wait for user input
    # save playlist to topics covered
    st.session_state.topics_covered[topic] = playlist_data[int(playlist_number)]["id"]['playlistId']
    # start a new thread for each upload_videos call
    # st.write(f"loading in video data from the playlist {playlist_data[int(playlist_number)]['id']['playlistId']}")
    # start_video_upload_thread(playlist_data[int(playlist_number)]["id"]['playlistId'])
    st.write(f"Learning from playlist {playlist_data[int(playlist_number)]['title']}...")
    upload_videos(playlist_data[int(playlist_number)]["id"]['playlistId'])
    st.success(f"Finished learning from playlist {playlist_data[int(playlist_number)]['title']}!")
    # threading.Thread(target=upload_videos, args=(playlist_data[int(playlist_number)]["id"]['playlistId'],)).start()
    st.session_state.stage = "playlist"
    st.rerun()


st.session_state["stage"] == "end"
# next, for every topic playlist pair in topics covered, assemble topic information
# """for topic in st.session_state.topics_covered:
#     st.write(topic)
#     topic_name = topic.keys()[0]
#     playlist_id = topic[topic_name]
#     st.write(playlist_id)
#     top_topic = search_playlist(playlist_id, topic_name, k=1) # maybe search on query instead of topic_name (or some combination)
#     info = {
#         "topic": topic,
#         "info": top_topic["text"],
#     }
#     st.session_state.topic_context_info.append(info)"""

# elif st.session_state["stage"] == "playlist_selected"
#     with st.sidebar:
#         st.title("Select Videos - each one takes a minute")
#         for playlist in st.session_state.playlist_data:
#             # Fetch the YouTube video thumbnail
#             thumbnail_url = playlist["thumbnail"]
#
#             # Display the thumbnail and checkbox
#             st.image(thumbnail_url, width=250)
#             checkbox_label = f"Select {playlist['title']}"
#
#             checkbox = st.checkbox(checkbox_label)
#             if checkbox:
#                 if "selected_playlists" not in st.session_state:
#                     st.session_state["selected_playlists"] = []
#                 st.session_state["selected_playlists"].append(playlist["id"])
#         if st.button("Confirm"):
#             for playlist_id in st.session_state.selected_playlists:
#                 # Start a new thread for each upload_videos call
#                 st.write(f"loading in video data from the playlist {playlist_id}")
#                 threading.Thread(target=upload_videos, args=(playlist_id,)).start()


# # Display a message while threads are running
# if st.session_state["video_threads"]:
#     if all_threads_done():
#         st.success("All video uploads completed!")
#         # Clear the list if needed
#         st.session_state["video_threads"].clear()
#     else:
#         st.info("Learning from videos...")

# Additional logic that should run after all threads are complete
# This block will run in the next iteration after all threads are done
# if not st.session_state["video_threads"]:
#     # Your code to execute after all uploads are done
#     pass

#         # we have the playlist with info
#         top_topic = search_playlist(playlist_id, query, k=1)
#         info = {
#             "topic": topic,
#             "info": top_topic["text"],
#         }
#         st.session_state.topic_context_info.append(info)
#         st.session_state["stage"] == "respond"
# elif st.session_state["stage"] == "respond":
#     generate_response = f"""
#                     Answer my question: "{query}"
#
#                     Using these facts from your knowledge:
#                     "{st.session_state.topic_context_info}"
#                     """
#     # Get the response from
#     #  the LLM call function
#     response_text, conversation, total_tokens, response = call_llm(
#         user_query=generate_response,
#         conversation=st.session_state.messages,
#         system_prompt=group_dict["B"],
#     )
#     st.session_state.messages.append({"role": "assistant", "content": response_text})
#
#     # Write the assistant response to the chat
#     st.chat_message("assistant").write(response_text)
#     st.session_state["end"] = True

# As long as query not empty make it input
while st.session_state["stage"] == "end":

    if query := st.chat_input():
        # Run the conversation with the user
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)

        # Get the response from the LLM call function
        response_text, conversation, total_tokens, response = call_llm(
            user_query=query,
            conversation=st.session_state.messages,  # Dropped system prompt here --> Bug prone?
        )

        # Update the session state messages with the assistant's response
        st.session_state.messages.append(
            {"role": "assistant", "content": response_text}
        )

        # Write the assistant response to the chat
        st.chat_message("assistant").write(response_text)
    else:
        break
# function names

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
