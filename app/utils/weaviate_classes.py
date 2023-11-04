default_class = {
    "class": "DefaultClass",
    "description": "Default class",
    "vectorizer": "text2vec-openai",
    "properties": [
        {
            "name": "text",
            "description": "Text field",
            "dataType": ["string"],
        }
    ]
}


yt_playlist_class = {
    "class": "YoutubePlaylist",
    "description": "Youtube Playlist",
    "vectorizer": "text2vec-openai",
    'properties': [
        {
            "name": "title",
            "description": "Title of the Youtube Playlist",
            "dataType": ["string"],
        },
        {
            "name": "playlistID",
            "description": "ID of the Youtube Playlist",
            "dataType": ["string"],
        },
        {
            "name": "description",
            "description": "Description of the Youtube Playlist. This description should be detailed and complete, "
                           "as it is used as a check to understand the knowledge within the playlist",
            "dataType": ["string"],
        }
    ]
}

yt_topic_class = {
    "class": "YoutubeTopic",
    "description": "This contains information from youtube videos, grouped by Topic. Chunks from this are searched "
                   "directly after the playlist class.",
    "vectorizer": "text2vec-openai",
    "properties": [
        {
            "name": "title",
            "description": "Title of the Youtube Video",
            "dataType": ["string"],
        },
        {
            "name": "videoID",
            "description": "ID of the Youtube Video",
            "dataType": ["string"],
        },
        {
            "name": "text",
            "description": "The relevant text for the topic.",
            "dataType": ["string"],
        },
        {
            "name": "startTime",
            "description": "The start time of the relevant text for the topic.",
            "dataType": ["int"],
        },
        {
            "name": "topic",
            "description": "Topic of the Youtube Video. This should be descriptive and include all relevant topics "
                           "covered by the chunk.",
            "dataType": ["string"],
        }
    ]
}
