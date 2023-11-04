import streamlit as st
from app.utils.weaviate_connector import db, create_default_class


st.title('Example Page')



new_class_name = st.text_input("Enter a class name")
if st.button("Create Class"):
    response = create_default_class(new_class_name)
    st.write(response)
