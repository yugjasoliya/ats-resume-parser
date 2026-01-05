#!/usr/bin/env python3
# Command-line interface for the ATS resume parser.
import os
import json
import argparse
from ats_core import read_text_from_file, build_json_profile, keyword_score

def main():
    parser = argparse.ArgumentParser(description='ATS Resume Parser CLI')
    parser.add_argument('--resume', required=True, help='Path to resume file (.pdf, .docx, .txt)')
    parser.add_argument('--job', required=False, help='Path to job description (.txt or .md)')
    parser.add_argument('--outdir', default='.', help='Output directory')
    args = parser.parse_args()

    text = read_text_from_file(args.resume)
    profile = build_json_profile(text)

    os.makedirs(args.outdir, exist_ok=True)
    profile_path = os.path.join(args.outdir, 'resume_profile.json')
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2)

    print('Saved:', profile_path)

    if args.job:
        with open(args.job, 'r', encoding='utf-8', errors='ignore') as f:
            jd = f.read()
        match = keyword_score(text, jd)
        match_path = os.path.join(args.outdir, 'job_match.json')
        with open(match_path, 'w', encoding='utf-8') as f:
            json.dump(match, f, indent=2)
        print('Saved:', match_path)

if __name__ == '__main__':
    main()
