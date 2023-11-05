import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from app.utils.config import YT_API_KEY

yt = build("youtube", "v3", developerKey=YT_API_KEY)


@st.cache_data()
def get_yt_playlists(query, k=5):
    # get playlist IDs, title, description, and thumbnail for top 5 playlists
    response = (
        yt.search()
        .list(part="snippet", q=query, type="playlist", maxResults=k)
        .execute()
    )
    playlists = []

    for item in response["items"]:
        playlists.append(
            {
                "id": item["id"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            }
        )
    return playlists


def get_videos(playlist_id):
    """
    Get all video titles, descriptions, IDs from a playlist
    :param playlist_id: playlist to get videos from
    :return:
    """
    response = (
        yt.playlistItems()
        .list(part="snippet", playlistId=playlist_id, maxResults=50)
        .execute()
    )
    videos = []
    for item in response["items"]:
        videos.append(
            {
                "id": item["snippet"]["resourceId"]["videoId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
            }
        )
    return videos


def get_transcript(videoID):
    """
    Get the transcript of a video
    :param videoID: ID of the video to get the transcript of
    :return:
    """
    transcript = YouTubeTranscriptApi.get_transcript(videoID)
    return transcript


def get_playlist_info(playlistID):
    """
    Get playlist title, description, id, and thumbnail from playlist ID
    :param playlistID:
    :return:
    """
    response = yt.playlists().list(part="snippet", id=playlistID).execute()
    playlist = response["items"][0]
    return {
        "id": playlist["id"],
        "title": playlist["snippet"]["title"],
        "description": playlist["snippet"]["description"],
        "thumbnail": playlist["snippet"]["thumbnails"]["default"]["url"],
    }
