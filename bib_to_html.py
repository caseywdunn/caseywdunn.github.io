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



# Keywords that get a filter button above the publication list, in display order.
# Entries are filtered by the union of selected keywords; with none selected all are shown.
FILTER_KEYWORDS = [
    'sequence-analysis',
    'cnidaria',
    'molecular-phylogenetics',
    'siphonophora',
    'new-sequence-data',
    'transcriptomics',
    'phylogenomics',
    'phylogenetic-comparative-methods',
    'morphology',
    'taxonomy',
    'animal-phylogeny',
    'metazoa',
    'genomics',
    'review',
    'deep-sea',
    'software',
    'development',
    'coloniality',
    'microscopy',
    'commentary',
    'popular',
]

HTML_HEADER = """

<!-- Publications Section -->
<section id="publications" class="bg-light-gray">
    <div class="container">
        <div class="row">
            <div class="col-lg-12 text-center">
                <h2 class="section-heading">Publications</h2>
            </div>
        </div>
"""

FILTER_SCRIPT = """
<script>
(function () {
    var buttons = document.querySelectorAll('#pub-filters .pub-filter');
    var clear = document.getElementById('pub-clear');
    var boxes = document.querySelectorAll('#pub-list .box');
    var count = document.getElementById('pub-count');

    function update() {
        var selected = [];
        buttons.forEach(function (b) {
            if (b.getAttribute('aria-pressed') === 'true') selected.push(b.dataset.keyword);
        });
        var shown = 0;
        boxes.forEach(function (box) {
            var kws = (box.dataset.keywords || '').split(' ');
            var match = selected.length === 0 || selected.some(function (k) { return kws.indexOf(k) !== -1; });
            box.hidden = !match;
            if (match) shown++;
        });
        clear.hidden = selected.length === 0;
        count.textContent = selected.length === 0 ? '' : 'Showing ' + shown + ' of ' + boxes.length + ' publications';
    }

    buttons.forEach(function (b) {
        b.addEventListener('click', function () {
            var on = b.getAttribute('aria-pressed') !== 'true';
            b.setAttribute('aria-pressed', on ? 'true' : 'false');
            b.classList.toggle('active', on);
            update();
        });
    });
    clear.addEventListener('click', function () {
        buttons.forEach(function (b) {
            b.setAttribute('aria-pressed', 'false');
            b.classList.remove('active');
        });
        update();
    });
    update();
})();
</script>
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

    # Convert LaTeX accented characters to Unicode
    # Handle multiple formats: {\accent letter}, \accent{letter}, \accent letter

    # Acute accents: \'
    text = re.sub(r"\\'\{([a-zA-Z])\}", lambda m: {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                                                     'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r"\{\\'\\s*([a-zA-Z])\}", lambda m: {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                                                        'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r"\\'([a-zA-Z])", lambda m: {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                                                'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}.get(m.group(1), m.group(0)), text)

    # Grave accents: \`
    text = re.sub(r'\\`\{([a-zA-Z])\}', lambda m: {'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                                                     'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\{\\`\\s*([a-zA-Z])\}', lambda m: {'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                                                        'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\\`([a-zA-Z])', lambda m: {'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                                                'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}.get(m.group(1), m.group(0)), text)

    # Tilde: \~
    text = re.sub(r'\\~\{([a-zA-Z])\}', lambda m: {'a': 'ã', 'n': 'ñ', 'o': 'õ', 'A': 'Ã', 'N': 'Ñ', 'O': 'Õ'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\{\\~\\s*([a-zA-Z])\}', lambda m: {'a': 'ã', 'n': 'ñ', 'o': 'õ', 'A': 'Ã', 'N': 'Ñ', 'O': 'Õ'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\\~([a-zA-Z])', lambda m: {'a': 'ã', 'n': 'ñ', 'o': 'õ', 'A': 'Ã', 'N': 'Ñ', 'O': 'Õ'}.get(m.group(1), m.group(0)), text)

    # Umlaut/diaeresis: \"
    text = re.sub(r'\\"\{([a-zA-Z])\}', lambda m: {'a': 'ä', 'e': 'ë', 'i': 'ï', 'o': 'ö', 'u': 'ü', 'y': 'ÿ',
                                                     'A': 'Ä', 'E': 'Ë', 'I': 'Ï', 'O': 'Ö', 'U': 'Ü', 'Y': 'Ÿ'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\{\\"\\s*([a-zA-Z])\}', lambda m: {'a': 'ä', 'e': 'ë', 'i': 'ï', 'o': 'ö', 'u': 'ü', 'y': 'ÿ',
                                                        'A': 'Ä', 'E': 'Ë', 'I': 'Ï', 'O': 'Ö', 'U': 'Ü', 'Y': 'Ÿ'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\\"([a-zA-Z])', lambda m: {'a': 'ä', 'e': 'ë', 'i': 'ï', 'o': 'ö', 'u': 'ü', 'y': 'ÿ',
                                                'A': 'Ä', 'E': 'Ë', 'I': 'Ï', 'O': 'Ö', 'U': 'Ü', 'Y': 'Ÿ'}.get(m.group(1), m.group(0)), text)

    # Circumflex: \^
    text = re.sub(r'\\\^\{([a-zA-Z])\}', lambda m: {'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                                                      'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\{\\\^\\s*([a-zA-Z])\}', lambda m: {'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                                                         'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'}.get(m.group(1), m.group(0)), text)
    text = re.sub(r'\\\^([a-zA-Z])', lambda m: {'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                                                 'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'}.get(m.group(1), m.group(0)), text)

    # Special Nordic/European characters
    text = re.sub(r'\{\\o\}', 'ø', text)  # o with stroke
    text = re.sub(r'\\o\b', 'ø', text)
    text = re.sub(r'\{\\O\}', 'Ø', text)  # O with stroke
    text = re.sub(r'\\O\b', 'Ø', text)
    text = re.sub(r'\{\\aa\}', 'å', text)  # a with ring
    text = re.sub(r'\\aa\b', 'å', text)
    text = re.sub(r'\{\\AA\}', 'Å', text)  # A with ring
    text = re.sub(r'\\AA\b', 'Å', text)
    text = re.sub(r'\{\\ae\}', 'æ', text)  # ae ligature
    text = re.sub(r'\\ae\b', 'æ', text)
    text = re.sub(r'\{\\AE\}', 'Æ', text)  # AE ligature
    text = re.sub(r'\\AE\b', 'Æ', text)
    text = re.sub(r'\{\\ss\}', 'ß', text)  # German sharp s
    text = re.sub(r'\\ss\b', 'ß', text)

    # Cedilla: \c
    text = re.sub(r'\{\\c\{([cC])\}\}', lambda m: 'ç' if m.group(1) == 'c' else 'Ç', text)
    text = re.sub(r'\\c\{([cC])\}', lambda m: 'ç' if m.group(1) == 'c' else 'Ç', text)

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

    # First clean LaTeX sequences
    author_str = clean_tex(author_str)

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

    def entry_keywords(entry):
        return [k.strip() for k in entry.get('keywords', '').split(',') if k.strip()]

    counts = {}
    for entry in entries:
        for k in entry_keywords(entry):
            counts[k] = counts.get(k, 0) + 1

    # 3. Generate HTML
    with open(output_html, 'w', encoding='utf-8') as out:
        out.write(HTML_HEADER)

        # Keyword filter bar
        out.write('<p id="pub-filter-hint" class="text-center text-muted">Select keywords below to filter publications.</p>\n')
        out.write('<div id="pub-filters" class="text-center" role="group" aria-label="Filter publications by keyword">\n')
        for k in FILTER_KEYWORDS:
            if k not in counts:
                print(f"Warning: filter keyword '{k}' is not used by any entry", file=sys.stderr)
                continue
            label = k.replace('-', ' ')
            out.write(f'<button type="button" class="btn btn-default btn-sm pub-filter" data-keyword="{k}" aria-pressed="false">{label} <span class="badge">{counts[k]}</span></button>\n')
        out.write('<button type="button" id="pub-clear" class="btn btn-link btn-sm" hidden>Show all</button>\n')
        out.write('</div>\n')
        out.write('<p id="pub-count" class="text-center text-muted" aria-live="polite"></p>\n')
        out.write('<div id="pub-list">\n')

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
            code = [u.strip() for u in entry.get('code_repo', '').split(',') if u.strip()]
            data = [u.strip() for u in entry.get('data_repo', '').split(',') if u.strip()]
            cover = entry.get('cover_article', '')
            isbn = entry.get('isbn', '') if entry.get('ENTRYTYPE', '') == 'book' else ''

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
            keywords = ' '.join(entry_keywords(entry))
            out.write(f'<div class="box" data-keywords="{keywords}"><div class="box-title"></div><div class="box-body">\n')
            out.write(f'<p class="text-muted">{citation}')

            # --- Links Section ---
            
            # DOI
            clean_doi = ''
            if doi:
                clean_doi = doi.replace('http://dx.doi.org/', '').replace('https://doi.org/', '')
                out.write(f' <a href="https://doi.org/{clean_doi}">doi:{clean_doi}</a>.')

            # URL, unless it just restates the DOI
            if url and (not clean_doi or clean_doi not in url):
                out.write(f' <a href="{url}">Link</a>.')

            # ISBN (books only)
            if isbn:
                out.write(f' ISBN: {isbn}.')


            # Preprint
            if preprint:
                # Extract ID if it's a URL
                out.write(f' Preprint: <a href="{preprint}">Link</a>.')
            
            # Code
            if code:
                label = 'Git code repository' if len(code) == 1 else 'Git code repositories'
                links = ', '.join(f'<a href="{u}">{u}</a>' for u in code)
                out.write(f' {label}: {links}.')
            if data:
                label = 'Data repository' if len(data) == 1 else 'Data repositories'
                links = ', '.join(f'<a href="{u}">{u}</a>' for u in data)
                out.write(f' {label}: {links}.')
            
            # Cover Article
            if cover and cover.lower() == 'true':
                out.write(' <b>(Cover Article)</b>')

            # Close HTML Box
            out.write('</p>\n')
            out.write('</div><div class="box-footer"> </div></div>\n\n')

        out.write('</div>\n')
        out.write(FILTER_SCRIPT)
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