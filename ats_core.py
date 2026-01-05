#!/usr/bin/env python3
# Core utilities for a lightweight ATS-like resume parser.

import os
import re
from typing import List, Dict, Any, Tuple

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None

SECTION_HEADERS = [
    'summary', 'objective', 'education', 'experience', 'work experience',
    'professional experience', 'projects', 'skills', 'certifications',
    'publications', 'awards', 'achievements', 'languages', 'interests'
]

COMMON_SKILLS = {
    'sql', 'python', 'excel', 'microsoft excel', 'power bi', 'tableau',
    'jira', 'confluence', 'pandas', 'numpy', 'matplotlib', 'seaborn',
    'scikit-learn', 'machine learning', 'statistics', 'html', 'css',
    'javascript', 'git', 'github', 'agile', 'stakeholder management',
    'financial analysis', 'market research', 'data analysis',
    'business intelligence'
}

def read_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path.lower())[1]
    text = ''
    if ext == '.pdf':
        if PdfReader is None:
            raise RuntimeError('PyPDF2 not available. Install with: pip install PyPDF2')
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text() or ''
                text += '\n' + page_text
    elif ext in ('.docx', '.doc'):
        if Document is None:
            raise RuntimeError('python-docx not available. Install with: pip install python-docx')
        if ext == '.doc':
            raise ValueError('.doc not supported; please convert to .docx')
        doc = Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
    elif ext in ('.txt', '.md'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
    else:
        raise ValueError('Unsupported file type: ' + ext)

    # normalize whitespace
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\u00A0', ' ', text)
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r' *\n *', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_lines(text: str) -> List[str]:
    return [l.strip() for l in text.split('\n') if l.strip()]

def extract_contact_info(text: str) -> Dict[str, Any]:
    email_regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    phone_regexes = [
        r'(?:\+?91[\- ]?)?(?:0[\- ]?)?[6-9]\d{9}',                         # India mobile
        r'\+\d{1,3}[\- ]?\(?\d{1,4}\)?[\- ]?\d{3,4}[\- ]?\d{3,4}'          # generic intl
    ]
    url_regex = r'https?://[\w\-./?=&%#]+'

    emails = re.findall(email_regex, text, flags=re.I)
    phones = []
    for rgx in phone_regexes:
        phones.extend(re.findall(rgx, text, flags=re.I))
    phones = list(dict.fromkeys([re.sub(r'\s+', ' ', p).strip() for p in phones]))
    urls = re.findall(url_regex, text)

    linkedin = [u for u in urls if 'linkedin.com' in u][:1]
    github = [u for u in urls if 'github.com' in u][:1]
    portfolio = [u for u in urls if ('linkedin.com' not in u and 'github.com' not in u)][:3]

    return {
        'emails': list(dict.fromkeys(emails)),
        'phones': phones,
        'linkedin': linkedin,
        'github': github,
        'portfolio': portfolio
    }

def locate_sections(lines: List[str]) -> Dict[str, Tuple[int, int]]:
    indices = []
    for idx, line in enumerate(lines):
        ll = line.lower().strip(': ').strip()
        for header in SECTION_HEADERS:
            if ll == header or ll.startswith(header):
                indices.append((header, idx))
                break
    indices.sort(key=lambda x: x[1])
    sections = {}
    for i, (header, start) in enumerate(indices):
        end = indices[i + 1][1] if i + 1 < len(indices) else len(lines)
        sections[header] = (start + 1, end)
    return sections

def guess_name(lines: List[str]) -> str:
    for i in range(min(7, len(lines))):
        line = lines[i]
        if len(line) > 70:
            continue
        if re.search(r'@|http|www', line, flags=re.I):
            continue
        if line.lower().strip() in SECTION_HEADERS:
            continue
        words = [w for w in re.split(r'\s+', line) if w]
        if 1 <= len(words) <= 5:
            caps = sum(1 for w in words if w[0:1].isupper())
            if caps / len(words) >= 0.6:
                if not re.fullmatch(r'[A-Z ]{2,}', line):
                    return line
    return ''

def parse_skills(text: str, sections: Dict[str, Tuple[int, int]], lines: List[str]) -> List[str]:
    skills = []
    if 'skills' in sections:
        s, e = sections['skills']
        block = ' '.join(lines[s:e])
        parts = re.split(r',|;|\|/|\n|\u2022|•|-', block)
        for p in parts:
            token = p.strip().lower()
            if token and len(token) <= 40:
                skills.append(token)
    else:
        lt = text.lower()
        for sk in COMMON_SKILLS:
            if sk in lt:
                skills.append(sk)
    out, seen = [], set()
    for s in skills:
        if s not in seen:
            out.append(s); seen.add(s)
    return out

def parse_education(lines: List[str], sections: Dict[str, Tuple[int, int]]) -> List[Dict[str, Any]]:
    entries = []
    if 'education' not in sections:
        return entries
    s, e = sections['education']
    current = {}
    for line in lines[s:e]:
        ll = line.lower()
        if re.search(r'\b(b\.?e\.?|b\.?tech|bachelor|m\.?e\.?|m\.?tech|master|mba|bsc|msc|phd)\b', ll):
            if current:
                entries.append(current); current = {}
            current['degree'] = line
            continue
        m = re.findall(r'(20\d{2}|19\d{2})', line)
        if m:
            current['year'] = m[-1]
        if re.search(r'university|college|institute|iit|nit', ll):
            current['institution'] = line
        g = re.search(r'(?:cgpa|gpa|percentage)[: ]+([0-9.]{1,4})', ll)
        if g:
            current['grade'] = g.group(1)
    if current:
        entries.append(current)
    return entries

def parse_dates(line: str) -> str:
    ll = line.lower()
    month_pat = r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)'
    year_pat = r'(?:19|20)\d{2}'
    patterns = [
        month_pat + r' *' + year_pat + r' *(?:-|to) *' + month_pat + r' *' + year_pat,
        month_pat + r' *' + year_pat + r' *(?:-|to) *present',
        year_pat + r' *(?:-|to) *' + year_pat,
        year_pat + r' *(?:-|to) *present',
    ]
    for p in patterns:
        m = re.search(p, ll)
        if m:
            return m.group(0)
    return ''

def parse_experience(lines: List[str], sections: Dict[str, Tuple[int, int]]) -> List[Dict[str, Any]]:
    entries = []
    key = None
    for k in ['experience', 'work experience', 'professional experience']:
        if k in sections:
            key = k; break
    if not key:
        return entries
    s, e = sections[key]
    cur = {'bullets': []}
    for line in lines[s:e]:
        if not line.strip():
            continue
        if re.match(r'^[-*•] ', line):
            cur.setdefault('bullets', []).append(line.lstrip('-*• '))
            continue
        dr = parse_dates(line)
        if dr:
            cur['dates'] = dr; continue
        if re.search(r'@| at ', line.lower()) or (sum(1 for w in line.split() if w[:1].isupper()) >= 3 and len(line.split()) <= 12):
            if cur.get('role') or cur.get('company') or cur.get('bullets'):
                entries.append(cur)
            cur = {'bullets': []}
            m = re.split(r'\s@\s|\s at \s', line, flags=re.I)
            if len(m) == 2:
                cur['role'] = m[0].strip(); cur['company'] = m[1].strip()
            else:
                m2 = re.split(r'\s-\s|\s\|\s', line)
                if len(m2) == 2:
                    cur['role'] = m2[0].strip(); cur['company'] = m2[1].strip()
                else:
                    cur['role'] = line.strip()
            continue
        if len(line) > 10:
            cur.setdefault('description', []).append(line)
    if cur.get('role') or cur.get('company') or cur.get('bullets'):
        entries.append(cur)
    return entries

def parse_certifications(lines: List[str], sections: Dict[str, Tuple[int, int]]) -> List[str]:
    items = []
    if 'certifications' not in sections:
        return items
    s, e = sections['certifications']
    for line in lines[s:e]:
        token = line.strip('-*• ').strip()
        if token:
            items.append(token)
    return items

def parse_languages(lines: List[str], sections: Dict[str, Tuple[int, int]]) -> List[str]:
    items = []
    if 'languages' not in sections:
        return items
    s, e = sections['languages']
    block = ' '.join(lines[s:e])
    parts = re.split(r',|;|\|/|\n|\u2022|•|-', block)
    for p in parts:
        t = p.strip()
        if t:
            items.append(t)
