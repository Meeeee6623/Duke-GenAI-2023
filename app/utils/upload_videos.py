"""
Code to chunk and upload videos to Weaviate
"""
from app.utils.data_changes import upload_topic
from app.utils.queries import check_video
from app.utils.youtube import get_videos, get_transcript
from app.utils.openai_connector import get_video_topics


def upload_videos(playlist_id):
    """
    Upload all videos from a playlist to Weaviate
    :param playlist_id: the playlist to upload videos from
    :return:
    """
    # get all videos from playlist
    videos = get_videos(playlist_id)
    all_topics = []
    for video in videos:
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
    return all_topics


if __name__ == "__main__":
    # get playlist id from first arg
    import sys
    playlist_id = sys.argv[1]
    print(upload_videos(playlist_id))