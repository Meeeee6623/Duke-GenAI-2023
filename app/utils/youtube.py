from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from app.utils.config import YT_API_KEY

yt = build("youtube", "v3", developerKey=YT_API_KEY)


def get_yt_playlists(query, num_playlists=5):
    # get playlist IDs, title, description, and thumbnail for top 5 playlists
    response = (
        yt.search()
        .list(part="snippet", q=query, type="playlist", maxResults=num_playlists)
        .execute()
    )
    playlists = []

    for item in response["items"]:
        playlists.append(
            {
                "id": item["id"]["playlistId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "thumbnail": item["snippet"]["thumbnails"]["default"]["url"],
            }
        )
    return playlists


# get texts for system prompt
def get_yt_playlist_texts(query, num_playlists=5):
    response = (
        yt.search()
        .list(part="snippet", q=query, type="playlist", maxResults=num_playlists)
        .execute()
    )
    playlist_texts = []

    for item in response["items"]:
        playlist_id = item["id"]["playlistId"]
        description = item["snippet"]["description"]
        playlist_texts.append(f"ID: {playlist_id}, Description: {description} ")

    return playlist_texts


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
    Get playlist title, description, and thumbnail from playlist ID
    :param playlistID:
    :return:
    """
    response = yt.playlists().list(part="snippet", id=playlistID).execute()
    playlist = response["items"][0]
    return {
        "title": playlist["snippet"]["title"],
        "description": playlist["snippet"]["description"],
        "thumbnail": playlist["snippet"]["thumbnails"]["default"]["url"],
    }
