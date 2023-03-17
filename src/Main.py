from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from helper_functions import read_render_markdown_file, read_toml_file
from sidebar import create_sidebar

config = read_toml_file()

APP_TITLE = config["st-app"]["APP_TITLE"]
SUB_TITLE = config["st-app"]["SUB_TITLE"]

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    menu_items={
        "About": "Created with love & care at DataBooth - www.databooth.com.au"
    },
)


def create_app_header(app_title, subtitle=None):
    st.header(app_title)
    if subtitle is not None:
        st.subheader(subtitle)
    return None


def initialise_authentication():
    with open("./src/auth.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    name, authentication_status, username = authenticator.login("Login", "sidebar")
    return name, authentication_status, username, authenticator


name, authentication_status, username, authenticator = initialise_authentication()

if st.session_state["authentication_status"] is None:
    st.sidebar.warning("Please enter your username and password")
elif st.session_state["authentication_status"] is False:
    st.sidebar.error("Username/password is incorrect")
elif st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.write(f'*{st.session_state["name"]}* is logged in')
    create_app_header(APP_TITLE, SUB_TITLE)
    create_sidebar()
    read_render_markdown_file("docs/app_main.md", output="streamlit")
