"""
Contains various weaviate queries relating to classes
"""
from .weaviate_connector import db


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
