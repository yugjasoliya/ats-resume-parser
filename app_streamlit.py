
#!/usr/bin/env python3
import streamlit as st
import json
from ats_core import read_text_from_file, build_json_profile
import tempfile
import os

# Configure the page
st.set_page_config(page_title='ATS Resume Parser', layout='wide')
st.title('ATS Resume Parser (No JD)')

# File uploader
resume_file = st.file_uploader(
    'Upload your resume (.pdf/.docx/.txt)',
    type=['pdf', 'docx', 'txt']
)

# When a file is uploaded, process it
if resume_file is not None:
    # Save uploaded file to a temporary path so we can read it
    suffix = os.path.splitext(resume_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    # Read text and parse profile
    text = read_text_from_file(tmp_path)
    profile = build_json_profile(text)

    # Show parsed JSON
    st.subheader('Parsed Profile')
    st.json(profile)

    # Download button for JSON
    st.download_button(
        label='Download resume_profile.json',
        data=json.dumps(profile, indent=2),
        file_name='resume_profile.json',
        mime='application/json'
    )

# Small privacy note
st.caption('Your file is processed on the server; no external APIs are called.')
