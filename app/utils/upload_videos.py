"""
Code to chunk and upload videos to Weaviate
"""
from app.utils.data_changes import upload_topic, create_playlist
from app.utils.queries import check_video
from app.utils.youtube import get_videos, get_transcript, get_playlist_info
from app.utils.openai_connector import get_video_topics, call_llm
import streamlit as st


def upload_videos(playlist_id):
    """
    Upload all videos from a playlist to Weaviate
    :param playlist_id: the playlist to upload videos from
    :return:
    """
    print(f"Uploading videos from playlist {playlist_id}")
    # get all videos from playlist
    videos = get_videos(playlist_id)
    playlist_info = get_playlist_info(playlist_id)
    # get playlist description with openai call on video titles
    synthetic_description = call_llm(f"""
    Write a playlist description for a playlist titled "{playlist_info['title']}".
    The playlist contains the following videos:
    {[video['title'] for video in videos]}
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
    playlist_description = synthetic_description[0]
    print(f"Playlist description is {playlist_description}")
    # upload playlist to weaviate
    create_playlist(playlist_id, playlist_info["title"], playlist_description)
    print(f"Uploaded playlist object for {playlist_info['title']} to weaviate!")
    all_topics = []
    for video in videos:
        try:
            print(f"Uploading video {video['title']}")
            # check if video already exists in weaviate
            video_exists = check_video(video["id"])
            if video_exists:
                print(f"Video {video['title']} already exists in Weaviate")
                continue
            # get transcript
            transcript = get_transcript(video["id"])
            print(f"Transcript for {video['title']} is {len(transcript)} words long")
            # chunk transcript
            topics = get_video_topics(transcript)
            all_topics.extend(topics)
            # upload topics to weaviate
            for topic in topics:
                topic["playlistID"] = playlist_id
                topic["videoID"] = video["id"]
                topic["title"] = video["title"]
                upload_topic(topic)
        except:
            continue
    st.success(f"Uploaded all videos from playlist {playlist_info['title']} successfully!")
    st.balloons()
    return all_topics


if __name__ == "__main__":
    # get playlist id from first arg
    import sys

    playlist_id = sys.argv[1]
    print(upload_videos(playlist_id))
