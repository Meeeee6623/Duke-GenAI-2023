"""
Contains utils for manipulating data from streamlit data editor
"""
import pandas as pd

from app.utils.queries import get_all_chunks


def get_edited_data(original_data, changed_rows):
    # Get the edited rows
    edited_rows = changed_rows.get("edited_rows", {})

    # Prepare a list to store tuples of (dict[uuid: list[dict[field: new_value]])
    edited_data = {}

    # Iterate through the edited_rows
    for row_index, change in edited_rows.items():
        # Get the corresponding row from the original DataFrame
        original_row = original_data.iloc(0)[int(row_index)]

        # Get the uuid and new chunkContent
        uuid = original_row["id"]

        # Append the changed values to the dict
        edited_data[uuid] = change

    return edited_data


def get_deleted_ids(original_data, deleted_indexes):
    """
    Gets the uuids of the deleted rows, given the indexes of the deleted rows.
    """
    deleted_ids = []
    for row_index in deleted_indexes:
        deleted_ids.append(original_data.iloc(0)[int(row_index)]["id"])
    return deleted_ids


def get_new_data(new_rows):
    """
    Gets the new rows, given the new rows.
    """
    new_data = []
    # get row value for each new row
    for i in range(len(new_rows)):
        new_data.append(new_rows[i])
    return new_data


def get_all_chunks_df(class_name):
    all_chunks = get_all_chunks(class_name)
    try:
        df = pd.DataFrame.from_records(all_chunks)
        ids = [d["_additional"]["id"] for d in all_chunks]
        df = df.assign(id=ids)
        df.drop(columns=["_additional"], inplace=True)
        return df
    except Exception as e:
        print(e)
        return "No chunks found"
