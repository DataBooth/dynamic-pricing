
import streamlit as st
from helper_functions import read_render_markdown_file
from pathlib import Path

tab0, tab1 = st.tabs(["Page 1", "Page 2"])


with tab0:
    read_render_markdown_file("docs/app_idea_page1.md", "streamlit")


with tab1: 
    read_render_markdown_file("docs/app_idea_page2.md", output="streamlit")