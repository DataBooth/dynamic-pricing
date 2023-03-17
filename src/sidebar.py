import streamlit as st


def create_sidebar():
    st.sidebar.markdown("## __Sidebar:__")

    st.sidebar.date_input(label="Choose a date:")

    st.sidebar.slider(label="Take me for a slide...")
    return None