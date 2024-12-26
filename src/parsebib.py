from pybtex.database.input import bibtex
import os
from pathlib import Path
import requests


def convert_latex_diacritics(text):
    replacements = [
        ('{\\&}', '&'),
        ('{\\"{a}}', 'ä'),
        ('{\\~{a}}', 'ã'), # {\~{a}} Guimar{\~{a}}es
        ('{\\~\\{a\\}}', 'ã'),  # For {\~{a}}
        ('\\~{a}', 'ã'),        # Another variation
        ('\\\'o', 'ó'),
        ('\\\'i', 'í'),
        ('\\\'a', 'á'),
        ('{\\\'o}', 'ó'),
        ("{\\'{o}}", "ó"), # {\'{o}}
        ('{\\\'i}', 'í'),
        ("{\\'{\\i}}", "í"), # {\'{\i}}
        ('{\\\'a}', 'á'),
        ('{\\"u}', 'ü'),
        ('{\\"o}', 'ö'),
        ('{\\"O}', 'Ö'),
        ('{\\"{u}}', 'ü'),
        ('{\\"{o}}', 'ö'),
        ('{\\"{O}}', 'Ö'),
        ('{\"O}', 'Ö'),
        ('{\\c{c}}', 'ç'),
        ('{\\`{e}}', 'è'), # {\`{e}}
        ('{\\ae}', 'æ'), # {\ae}
        ('{-}', '-'),
    ]
    
    result = text
    for old, new in replacements:
        result = result.replace(old, new)
    return result


def get_initial_block(name: str) -> str:
    """
    Convert a hyphenated first name into initials, e.g.:
    'Klaas-Jan' -> 'K.J.'
    'Margaret-Anne' -> 'M.A.'
    """
    parts = name.split('-')
    letters = [p[0].upper() for p in parts if p]
    return ".".join(letters) + "." if letters else ""

def format_author(author):
    # Take only the first element in author.first_names, if any
    if author.first_names:
        main_first = convert_latex_diacritics(author.first_names[0])
        initial_block = get_initial_block(main_first)
    else:
        initial_block = ""

    # Join all last names into one string
    last_block = ' '.join(convert_latex_diacritics(ln) for ln in author.last_names)

    full_name = f"{initial_block} {last_block}".strip()

    # Special case for F. Calefato
    if full_name.lower() == "f. calefato":
        return f"\"***{full_name}***\""
    return full_name


def clean_latex_markup(text):
    return text.replace('{', '').replace('}', '').replace('\\&', '&')


def parse_bib(bib_file):
    if not os.path.exists(bib_file):
        raise FileNotFoundError(f"BibTeX file not found: {bib_file}")
    
    parser = bibtex.Parser()
    bib_data = parser.parse_file(bib_file)
    
    publications = []
    for _, entry in bib_data.entries.items():
        # filter out entries where publisher = {Zenodo} or journal = {CoRR}
        if 'zenodo' in entry.fields.get('publisher', '').lower()  or 'corr' in entry.fields.get('journal', '').lower():
            continue

        if entry.key == 'DBLP:conf/icgse/2019':
            continue

        if entry.type == 'proceedings':
            authors = [format_author(editor) for editor in entry.persons.get('editor', [])]
            venue = entry.fields.get('publisher', '')
            title = clean_latex_markup(entry.fields.get('title', ''))
        elif entry.type == 'inbook':
            authors = [format_author(author) for author in entry.persons.get('author', [])]
            venue = entry.fields.get('title', '')
            title = clean_latex_markup(entry.fields.get('chapter', ''))
        else:
            authors = [format_author(author) for author in entry.persons.get('author', [])]
            venue = entry.fields.get('journal', '') or entry.fields.get('booktitle', '')
            title = clean_latex_markup(entry.fields.get('title', ''))

        pub = {
            'title': title,
            'authors': authors,
            'journal': clean_latex_markup(convert_latex_diacritics(venue)),
            'doi': entry.fields.get('doi', '').replace('\\_', '_'),
        }
        
        if 'year' in entry.fields:
            pub['date'] = entry.fields['year']
            
        if 'volume' in entry.fields:
            pub['journal'] += f", vol. {entry.fields['volume']}"
        if 'number' in entry.fields:
            pub['journal'] += f", no. {entry.fields['number']}"
            
        publications.append(pub)

    return {'publications': publications}


def format_yaml_content(data):
    output = "    publications:\n"
    for pub in data['publications']:
        output += f"      - title: \"{pub['title']}\"\n"
        output += "        authors:\n"
        for author in pub['authors']:
            output += f"          - {author}\n"
        output += f"        date: {pub['date']}\n"
        output += f"        journal: \"{pub['journal']}\"\n"
        if pub.get('doi'):
            output += f"        doi: {pub['doi']}\n"
    return output


def download_bib_from_dblp(file, url):
    try:
        response = requests.get(url, timeout=10)  # 10 second timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        with open(os.path.join(file), 'wb') as f:
            f.write(response.content)
            
    except requests.exceptions.Timeout:
        print(f"Warning: Request timed out while downloading from {url}")
        if not os.path.exists(file):
            raise FileNotFoundError(f"No existing BibTeX file found at {file}")
        else:
            print(f"Using existing BibTeX file at {file}")
            
    except requests.exceptions.RequestException as e:
        print(f"Warning: Failed to download BibTeX ({str(e)})")
        if not os.path.exists(file):
            raise FileNotFoundError(f"No existing BibTeX file found at {file}")
        else:
            print(f"Using existing BibTeX file at {file}")


def merge_bib_files(dblp_file, additional_file, output_file):
    with open(dblp_file, 'r') as f:
        dblp_content = f.read()
    with open(additional_file, 'r') as f:
        additional_content = f.read()

    with open(output_file, 'w') as f:
        f.write(dblp_content)
        f.write('\n\n')
        f.write(additional_content)


if __name__ == '__main__':
    # author's DBLP URL
    dblp_url = 'https://dblp.org/pid/48/5662.bib?param=1'

    script_dir = Path(__file__).parent
    dblp_file = os.path.join(str(script_dir), 'bibliography', 'dblp.bib')
    additional_entries = os.path.join(str(script_dir), 'bibliography', 'not_in_dblp.bib')
    bib_file = os.path.join(str(script_dir), 'bibliography', 'publications.bib')
    yaml_file = os.path.join(str(script_dir), 'bibliography', 'publications.yaml')
    
    try:
        download_bib_from_dblp(dblp_file, dblp_url)
        merge_bib_files(dblp_file, additional_entries, bib_file)
        publications = parse_bib(bib_file)
        with open(yaml_file, 'w') as f:
            f.write(format_yaml_content(publications))
    except FileNotFoundError as e:
        print(f"Error: {e}")