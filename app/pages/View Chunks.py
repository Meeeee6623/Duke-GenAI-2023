import streamlit as st

from app.utils.data_changes import delete_chunks, update_chunks, create_chunks, create_default_class
from app.utils.data_editor import get_edited_data, get_deleted_ids, get_new_data, get_all_chunks_df
from app.utils.queries import get_all_classes

st.set_page_config(page_title='View Chunks')

df = None  # initialize df to None

class_names = get_all_classes()
class_name = st.selectbox(
    "Class Name", class_names, key="chunk_Editor"
)
custom_class_name = st.text_input("Custom Class Name", key="custom_class_name")
if custom_class_name:
    if st.button("Create Class"):
        class_name = custom_class_name
        create_default_class(class_name=class_name)
        create_chunks(class_name=class_name, new_chunks=[{"text": ""}])
        st.success(f"Class {class_name} created successfully")
        st.rerun()

st.write(f"Finding all chunks for class: {class_name}")
df = get_all_chunks_df(class_name=class_name)
try:
    st.data_editor(df, key="data_editor", num_rows="dynamic")
except Exception as e:
    st.write(st.write("No chunks found for this class"))
    create_chunks(class_name=class_name, new_chunks=[{"text": ""}])
    st.rerun()


st.write("Here's your changes")
st.write(st.session_state["data_editor"])  # edited data
if st.button("Submit Changes"):
    # dblink.update_chunks(edited_df, class_name)
    edited_data = get_edited_data(
        original_data=df, changed_rows=st.session_state["data_editor"]
    )
    deleted_row_ids = get_deleted_ids(
        original_data=df, deleted_indexes=st.session_state["data_editor"].get("deleted_rows", [])
    )
    new_data = get_new_data(
        new_rows=st.session_state["data_editor"].get("added_rows", [])
    )
    delete_chunks(class_name=class_name, ids=deleted_row_ids)
    update_chunks(class_name=class_name, new_values=edited_data)
    create_chunks(class_name=class_name, new_chunks=new_data)
    st.success(f"Changes to {class_name} have been submitted.")
    # update data editor with live reload
    df = get_all_chunks_df(class_name=class_name)
    st.write("Reloading data editor...")
    st.rerun()
