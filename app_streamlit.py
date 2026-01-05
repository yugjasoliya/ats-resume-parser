#!/usr/bin/env python3
import streamlit as st
import json
from ats_core import read_text_from_file, build_json_profile
import tempfile
import os

st.set_page_config(page_title='ATS Resume Parser', layout='wide')
st.title('ATS Resume Parser (No JD)')

resume_file = st.file_uploader('Upload your resume (.pdf/.docx/.txt)', type=['pdf','docx','txt'])

if resume_file is not None:
    suffix = os.path.splitext(resume_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    text = read_text_from_file(tmp_path)
    profile = build_json_profile(text)

    st.subheader('Parsed Profile')
    st.json(profile)

    st.download_button(
        'Download resume_profile.json',
        data=json.dumps(profile, indent=2),
        file_name='resume_profile.json',
        mime='application/json'
    )

st.caption('Your file is processed on the server; no external APIs are called.')
