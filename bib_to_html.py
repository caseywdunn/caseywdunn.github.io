import bibtexparser
from bibtexparser.bparser import BibTexParser
import sys
import argparse
import re

# Example use
# conda create --name biblio python=3.14
# conda activate biblio
# conda install conda-forge::bibtexparser
#
# conda activate biblio
# python bib_to_html.py ../casey_dunn_cv/publications.bib _includes/publications.html



HTML_HEADER = """---
layout: default
title: Publications
permalink: /publications/
---

<!-- Publications Section -->
<section id="publications" class="bg-light-gray">
    <div class="container">
        <div class="row">
            <div class="col-lg-12 text-center">
                <h2 class="section-heading">Publications</h2>
            </div>
        </div>
"""

HTML_FOOTER = """
    </div>
</section>
"""

def clean_tex(text):
    """
    Converts basic LaTeX formatting to HTML.
    """
    if not text: return ""
    
    # Convert \textit{...} and \emph{...} to <i>...</i>
    text = re.sub(r'\\textit\{(.*?)\}', r'<i>\1</i>', text)
    text = re.sub(r'\\emph\{(.*?)\}', r'<i>\1</i>', text)
    
    # Convert LaTeX special chars
    text = text.replace(r'\&', '&')
    text = text.replace('--', '–') # dash
    text = text.replace('{', '').replace('}', '') # Strip protecting braces
    
    return text

def format_authors(author_str):
    """
    Converts "Dunn, C. W. and Oguchi, K." -> "Dunn CW, Oguchi K"
    """
    if not author_str: return ""
    
    authors = author_str.replace('\n', ' ').split(' and ')
    formatted = []
    
    for auth in authors:
        parts = auth.split(',')
        if len(parts) >= 2:
            surname = parts[0].strip()
            initials = parts[1].strip().replace('.', '').replace(' ', '')
            formatted.append(f"{surname} {initials}")
        else:
            formatted.append(auth) # Fallback
            
    return ", ".join(formatted)

def generate_html(input_bib, output_html):
    # 1. Parse BibTeX
    with open(input_bib, 'r', encoding='utf-8') as bib_file:
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.load(bib_file, parser=parser)

    entries = bib_database.entries
    
    # 2. Sort by Year (Descending)
    # Note: bibtexparser returns strings, so we sort safely
    entries.sort(key=lambda x: x.get('year', '0000'), reverse=True)

    # 3. Generate HTML
    with open(output_html, 'w', encoding='utf-8') as out:
        out.write(HTML_HEADER)
        
        for entry in entries:
            # Extract fields
            authors = format_authors(entry.get('author', ''))
            year = entry.get('year', '')
            title = clean_tex(entry.get('title', ''))
            journal = clean_tex(entry.get('journal', entry.get('booktitle', '')))
            volume = entry.get('volume', '')
            pages = entry.get('pages', '')
            doi = entry.get('doi', '')
            url = entry.get('url', '')
            preprint = entry.get('preprint', '')
            code = entry.get('code_repo', '')
            cover = entry.get('cover_article', '')
            
            # Build citation string
            # Example: "Dunn CW (2025) Title. Journal Vol:Pages."
            citation = f"{authors} ({year}) {title}. "
            
            if journal:
                citation += f"<i>{journal}</i>"
                if volume:
                    citation += f" {volume}"
                    if pages:
                        citation += f":{pages}"
                citation += "."
            
            # Start HTML Box
            out.write('<div class="box"><div class="box-title"></div><div class="box-body">\n')
            out.write(f'<p class="text-muted">{citation}')

            # --- Links Section ---
            
            # DOI
            if doi:
                clean_doi = doi.replace('http://dx.doi.org/', '').replace('https://doi.org/', '')
                out.write(f' <a href="https://doi.org/{clean_doi}">doi:{clean_doi}</a>.')
            # URL (only if no DOI, usually)
            elif url:
                out.write(f' <a href="{url}">Link</a>.')
            
            # Preprint
            if preprint:
                # Extract ID if it's a URL
                out.write(f' Preprint: <a href="{preprint}">Link</a>.')
            
            # Code
            if code:
                out.write(f' Git code repository: <a href="{code}">{code}</a>.')
            
            # Cover Article
            if cover and cover.lower() == 'true':
                out.write(' <b>(Cover Article)</b>')

            # Close HTML Box
            out.write('</p>\n')
            out.write('</div><div class="box-footer"> </div></div>\n\n')

        out.write(HTML_FOOTER)

    print(f"Successfully generated {output_html} from {input_bib}")

if __name__ == "__main__":
    # Argument parsing
    if len(sys.argv) != 3:
        print("Usage: python bib2html.py <input_bib> <output_html>")
        sys.exit(1)
        
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    generate_html(input_path, output_path)