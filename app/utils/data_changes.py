"""
Contains functions that update, create, or delete data in Weaviate
"""
from .weaviate_classes import default_class
from .weaviate_connector import db
from app.utils.queries import check_playlist


def create_playlist(playlist_id: str, title: str, description: str):
    """
    Create a playlist in Weaviate
    """
    if check_playlist(playlist_id):
        return {"error": "Playlist already exists"}
    new_playlist = {
        "playlistID": playlist_id,
        "title": title,
        "description": description,
    }
    try:
        db.data_object.create(data_object=new_playlist, class_name="YoutubePlaylist")
    except Exception as e:
        print(e)
        return {"error": "Playlist already exists"}
    return {"response": "Playlist created successfully"}


def upload_topic(topic: dict):
    """
    Upload a topic to Weaviate
    Topics have:
    - title (video title)
    - description
    - playlistID
    - videoID
    - text (real information returned)
    - startTime (start time of the video)
    - topic (descriptive topic name, searched)
    :param topic:
    :return:
    """
    try:
        db.data_object.create(data_object=topic, class_name="YoutubeTopic")
    except Exception as e:
        print(e)
        return {"error": "Topic already exists"}
    return {"response": "Topic created successfully"}


def create_default_class(class_name: str):
    """
    Create a class in Weaviate
    """
    new_class = default_class
    new_class["class"] = class_name
    try:
        db.schema.create_class(new_class)
    except Exception as e:
        print(e)
        return {"error": "Class already exists"}
    return {"response": "Class created successfully"}


def delete_class(class_name: str):
    """
    Delete a class in Weaviate
    """
    try:
        db.schema.delete_class(class_name)
    except Exception as e:
        print(e)
        return {"error": "Class does not exist"}
    return {"response": "Class deleted successfully"}


def update_chunks(class_name, new_values: dict[str: list[dict[str:str]]]):
    """
    Updates the values of a list of chunks of a class, used in streamlit playground
    Takes in a dict of the form chunk id: fields, new values
    """
    # ensure every field has the correct data type
    class_schema = db.schema.get(class_name)
    # get field types (dict[field_name: type])
    field_types = {
        field["name"]: field["dataType"][0] for field in class_schema["properties"]
    }
    # convert to python data types:
    for field in field_types.keys():
        data_type = field_types[field]
        if data_type == "text":
            field_types[field] = str
        elif data_type == "boolean":
            field_types[field] = bool
        elif data_type == "int" or data_type == "number":
            field_types[field] = int
        elif field_types[field] == "text[]":
            field_types[field] = list[str]
    for chunk_id in new_values.keys():
        # new values is a dict of the form chunk id: dict[fields: new_value]
        # get new data object (field: value) for all new values
        new_values_dict = new_values[chunk_id]
        # convert values to correct data type
        for field in new_values_dict.keys():
            # ensure type matches by casting
            new_values_dict[field] = field_types[field](new_values_dict[field])
        # update chunk in weaviate
        db.data_object.update(new_values_dict, class_name, chunk_id)


def delete_chunks(class_name, ids):
    """
    Deletes all chunks with the given ids
    """
    for id in ids:
        db.data_object.delete(uuid=id, class_name=class_name)


def create_chunks(class_name=None, new_chunks=None):
    """
    Adds given chunks to the database under the given class name
    """
    if class_name is None:
        raise Exception("class_name must be specified")
    if new_chunks is None:
        raise Exception("new_chunks must be specified")
    with db.batch(
            batch_size=20,
            num_workers=4,
            dynamic=True,
    ) as batch:
        for chunk in new_chunks:
            batch.add_data_object(
                data_object=chunk,
                class_name=class_name,
            )
