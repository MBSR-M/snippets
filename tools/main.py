#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
from datetime import date
import requests
from bs4 import BeautifulSoup


def fetch_files_and_folders(url, username, password):
    try:
        # Make a GET request with basic authentication
        response = requests.get(url, auth=(username, password))
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract links from <a> tags
        links = [a['href'] for a in soup.find_all('a', href=True)]

        # Separate files and folders
        files = [link for link in links if not link.endswith('/')]
        folders = [link for link in links if link.endswith('/')]

        return files, folders

    except Exception as e:
        return f"Error: {e}", []


def main():
    st.title("File and Folder Browser with Authentication")
    st.sidebar.title("Configuration")
    project_url = 'https://mpwz4-hes.mpwz4.prod.cyanconnode.com'
    # Input for URL, username, and password
    base_url = st.sidebar.text_input("Enter Base URL", f"{project_url}/logs/shared/")
    username = st.sidebar.text_input("Enter Username", "")
    password = st.sidebar.text_input("Enter Password", "", type="password")

    # Session state to keep track of the current URL
    if "current_url" not in st.session_state:
        st.session_state.current_url = base_url

    # Fetch files and folders when button is clicked
    if st.sidebar.button("Fetch Content"):
        if not username or not password:
            st.error("Please enter both username and password.")
        else:
            st.session_state.current_url = base_url
            files, folders = fetch_files_and_folders(st.session_state.current_url, username, password)

            if isinstance(files, str):  # If there's an error, display it
                st.error(files)
            else:
                display_content(files, folders, username, password, project_url)

    # Navigate to a folder
    if "navigate_to" in st.session_state and st.session_state.navigate_to:
        st.session_state.current_url = st.session_state.navigate_to
        files, folders = fetch_files_and_folders(st.session_state.current_url, username, password)
        display_content(files, folders, username, password, project_url)


def display_content(files, folders, username, password, project_url):
    st.write(f"Current URL: {st.session_state.current_url}")
    st.write("### Folders:")
    for folder in folders:
        # Create a button for each folder
        if st.button(folder, key=folder):
            st.session_state.navigate_to = project_url + folder

    st.write("### Files:")
    for file in files:
        st.write(file)


if __name__ == "__main__":
    main()
