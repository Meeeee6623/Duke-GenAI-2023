"""
Contains various weaviate queries relating to classes
"""
from app.utils.weaviate_connector import db


# function names
# weaviate query for top k playlists:
def get_top_k_playlists(query, k, threshold=None):
    """
    Gets the top k playlists from weaviate
    :param query: the query to search for
    :param k: the number of playlists to return
    :return: the top k playlists
    """
    near_text = {
        "concepts": [f"{query}"],
    }
    if threshold is not None:
        near_text["certainty"] = threshold
    playlists = (
        db.query.get("YoutubePlaylist", ["title", "description"])
        .with_limit(k)
        .with_near_text(near_text)
        .do()["data"]["Get"]["YoutubePlaylist"]
    )
    return playlists


# search through playlists for topic
def search_playlist(playlist_id, query, k):
    """
    Searches through a playlist for a given query
    :param playlist_id: the playlist to search through
    :param query: the query to search for
    :param k: the number of videos to return
    :return: the top k videos from the playlist
    """
    near_text = {
        "concepts": [f"{query}"],
    }
    where_filter = {
        "path": ["playlistID"],
        "operator": "Equal",
        "valueString": playlist_id,
    }
    videos = (
        db.query.get("YoutubeTopic", ["title", "description"])
        .with_limit(k)
        .with_where(where_filter)
        .with_near_text(near_text)
        .do()["data"]["Get"]["YoutubeVideo"]
    )
    return videos


def get_all_classes():
    """
    Get all classes in weaviate
    """
    schema = db.schema.get()
    return [c["class"] for c in schema["classes"]]


def get_all_chunks(class_name: str):
    """
    Gets all chunks for a given class using Weaviate cursor api
    :param class_name:
    :return:
    """
    # capitalize class name to follow GraphQL syntax
    class_name = class_name[0].upper() + class_name[1:]
    class_properties = db.schema.get(class_name)["properties"]
    field_names = [prop["name"] for prop in class_properties]
    try:
        cursor = None
        all_data = []
        data = []
        while True:
            query = (
                db.query.get(class_name, field_names)
                .with_additional(["id"])
                .with_limit(100)
            )
            if cursor is None:
                data = query.do()["data"]["Get"][class_name]
            else:
                data = query.with_after(cursor).do()["data"]["Get"][class_name]
            if data is None or len(data) == 0:
                break
            cursor = data[-1]["_additional"]["id"]
            all_data.extend(data)
        print(data)
    except Exception as e:
        print(e)
        return "No chunks found"
    if len(all_data) == 0:
        return "No chunks found"
    return all_data


def check_video(video_id):
    """
    Check if a video exists in weaviate
    :param video_id:
    :return: True if video exists, False otherwise
    """
    try:
        where_filter = {
            "path": ["videoID"],
            "operator": "Equal",
            "valueString": video_id,
        }
        query = db.query.get("YoutubeTopic", ["videoID"]).with_where(where_filter)
        data = query.do()["data"]["Get"]["YoutubeTopic"]
        if len(data) > 0:
            return True
    except Exception as e:
        print(e)
        return False
    return False


def check_playlist(playlist_id):
    """
    Check if a playlist exists in weaviate
    :param playlist_id:
    :return:
    """
    try:
        where_filter = {
            "path": ["playlistID"],
            "operator": "Equal",
            "valueString": playlist_id,
        }
        query = db.query.get("YoutubePlaylist", ["playlistID"]).with_where(where_filter)
        data = query.do()["data"]["Get"]["YoutubePlaylist"]
        if len(data) > 0:
            return True
    except Exception as e:
        print(e)
        return False
    return True
