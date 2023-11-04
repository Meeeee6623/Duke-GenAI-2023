from app.utils.weaviate_classes import yt_playlist_class, yt_topic_class
from app.utils.weaviate_connector import db

# make classes
reset = input("Reset YouTube classes? (y/n)")
if reset == "y":
    db.schema.delete_class(yt_playlist_class)
    db.schema.delete_class(yt_topic_class)
db.schema.create_class(yt_playlist_class)
db.schema.create_class(yt_topic_class)