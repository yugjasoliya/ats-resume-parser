#!/usr/bin/env python3
# Simple Streamlit app for ATS-style resume parsing.
import streamlit as st
import json
from ats_core import read_text_from_file, build_json_profile, keyword_score
import tempfile
import os

st.set_page_config(page_title='ATS Resume Parser', layout='wide')

st.title('ATS Resume Parser (Local)')

col1, col2 = st.columns(2)
with col1:
    resume_file = st.file_uploader('Upload your resume (.pdf/.docx/.txt)', type=['pdf','docx','txt'])
with col2:
    jd_text = st.text_area('Paste job description (optional)', height=200)

if resume_file is not None:
    # Save to a temp file
    suffix = os.path.splitext(resume_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name
    text = read_text_from_file(tmp_path)
    profile = build_json_profile(text)

    st.subheader('Parsed Profile')
    st.json(profile)

    if jd_text.strip():
        st.subheader('Job Match')
        match = keyword_score(text, jd_text)
        st.write(f"Coverage: **{match['coverage']}%**")
        st.write('Top Job Keywords:')
        st.write(', '.join(match['job_top_keywords']))
        st.write('Found in Resume:')
        st.write(', '.join(match['found_in_resume']))

    st.download_button('Download resume_profile.json', data=json.dumps(profile, indent=2), file_name='resume_profile.json', mime='application/json')
    if jd_text.strip():
        st.download_button('Download job_match.json', data=json.dumps(match, indent=2), file_name='job_match.json', mime='application/json')
