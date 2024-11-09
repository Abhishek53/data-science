import streamlit as st

# Add image to top right
# Add inline CSS and image to the top right\

# --- PAGE SETUP ---
st.set_page_config(layout="wide")
about_page = st.Page(
    "views/about_me.py",
    title="About Us",
    icon=":material/account_circle:",
)
project_2_page = st.Page(
    "views/chatbot.py",
    title="AI eSCR Multilingual Chatbot",
    icon=":material/smart_toy:",
    default=True,
)
project_1_page = st.Page(
    "views/petetion_identification.py",
    title="AI Petition Format Identification",
    icon=":material/receipt_long:",
)
project_3_page = st.Page(
    "views/petition_metadata_extraction.py",
    title="AI Petition Froms MetaData Extraction",
    icon=":material/quick_reference_all:",
    
)


# --- NAVIGATION SETUP [WITHOUT SECTIONS] ---
# pg = st.navigation(pages=[about_page, project_1_page, project_2_page])

# --- NAVIGATION SETUP [WITH SECTIONS]---
pg = st.navigation(
    {
        "Supreme Court Hackathon - 24": [project_2_page, project_1_page, project_3_page],
        "About Us": [about_page],
    }
)


# --- SHARED ON ALL PAGES ---
st.logo("https://upload.wikimedia.org/wikipedia/commons/3/34/EY_logo_2019.svg")
#st.sidebar.markdown("""⚡NYAYA MITRA 𓍝⚡""")
#st.sidebar.image("assets/sci_logo.png", width=100)

# Text and image HTML
sidebar_content = """
<div style="text-align: center;">
    <h2>NYAYA MITRA</h2>
    <img src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg" style="width: 100px;"/>  <!-- Adjust width as needed -->
</div>
"""

# Add the content to the sidebar
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)

# --- RUN NAVIGATION ---
pg.run()
