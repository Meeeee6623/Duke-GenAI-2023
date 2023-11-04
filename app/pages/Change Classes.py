import streamlit as st

st.set_page_config(page_title='Modify Classes')

from app.utils.data_changes import delete_chunks, update_chunks, create_chunks, create_default_class, delete_class
from app.utils.data_editor import get_edited_data, get_deleted_ids, get_new_data, get_all_chunks_df
from app.utils.queries import get_all_classes


all_classes = get_all_classes()
class_name = st.selectbox(
    "Class Name", all_classes, key="chunk_Editor"
)
custom_class_name = st.text_input("Custom Class Name", key="custom_class_name")
if custom_class_name:
    if st.button("Create Class"):
        class_name = custom_class_name
        create_default_class(class_name=class_name)
        create_chunks(class_name=class_name, new_chunks=[{"text": ""}])
        st.success(f"Class {class_name} created successfully")
        st.rerun()
else:
    st.write(f"Finding all chunks for class: {class_name}")
    all_chunks = get_all_chunks_df(class_name)
    st.dataframe(all_chunks)
    if st.button("Delete Class"):
        delete_class(class_name)
        st.success(f"Class {class_name} deleted successfully")
        st.rerun()
