import streamlit as st

# Add image to top right
# Add inline CSS and image to the top right\

# --- PAGE SETUP ---
from PIL import Image
im = Image.open("assets/ey-icon.png")

st.set_page_config(layout="wide", page_icon=im)
about_hackathon_page = st.Page(
    "views/about-hackathon.py",
    title="About Hackathon",
    icon=":material/account_circle:",
)
about_team_page = st.Page(
    "views/about-team.py",
    title="About Team",
    icon=":material/account_circle:",
)
project_2_page = st.Page(
    "views/chatbot.py",
    title="Graph RAG Multilingual Chatbot",
    #page_icon = im,
    #icon=":material/smart_toy:",
    default=True,
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Olympiad-Innovate-X'24 - Team Samaika": [project_2_page],
        "About": [about_hackathon_page, about_team_page],
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("https://upload.wikimedia.org/wikipedia/commons/3/34/EY_logo_2019.svg")
#st.sidebar.markdown("""⚡NYAYA MITRA 𓍝⚡""")
#st.sidebar.image("assets/sci_logo.png", width=100)

# Text and image HTML
sidebar_content = """
<div style="text-align: center;">
    <h2>AI Assitant</h2>
    <img src="https://cdn-icons-png.flaticon.com/128/9716/9716516.png" style="width: 100px;"/>  <!-- Adjust width as needed -->
</div>
"""

# Add the content to the sidebar
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)

# --- RUN NAVIGATION ---
pg.run()
