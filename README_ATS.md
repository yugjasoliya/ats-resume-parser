# Lightweight ATS Resume Parser

A simple local tool to parse resumes (PDF/DOCX/TXT), extract structured info, and optionally score keyword coverage vs a job description.

## Features
- Parse resume files locally (no data leaves your machine)
- Extract emails, phones, LinkedIn/GitHub/portfolio
- Detect sections: Summary, Skills, Education, Experience, Certifications, Languages
- Build `resume_profile.json` and (optionally) `job_match.json`
- Streamlit web UI for drag-and-drop

## Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scriptsctivate
pip install PyPDF2 python-docx streamlit
```

## CLI Usage
```bash
python ats_cli.py --resume /path/to/resume.pdf --outdir ./out
python ats_cli.py --resume /path/to/resume.pdf --job /path/to/job.txt --outdir ./out
```

## Streamlit App
```bash
streamlit run app_streamlit.py
```
Open the local URL shown in the terminal (typically http://localhost:8501).

## Notes
- If your PDF is image-only, run OCR or export to DOCX/TXT for best results.
- `.doc` files are not supported; convert to `.docx`.
- Section headers like `Skills`, `Education`, `Experience` improve accuracy.

## Extend
- Add domain-specific skills to `COMMON_SKILLS`.
- Improve role/company detection with NLP libraries (spaCy) if desired.
- Persist parsed profiles to a database for search & ranking.
