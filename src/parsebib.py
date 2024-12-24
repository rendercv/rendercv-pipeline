from pybtex.database.input import bibtex
import os
from pathlib import Path


def clean_latex_chars(text):
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
        main_first = clean_latex_chars(author.first_names[0])
        initial_block = get_initial_block(main_first)
    else:
        initial_block = ""

    # Join all last names into one string
    last_block = ' '.join(clean_latex_chars(ln) for ln in author.last_names)

    full_name = f"{initial_block} {last_block}".strip()

    # Special case for F. Calefato
    if full_name.lower() == "f. calefato":
        return f"\"***{full_name}***\""
    return full_name


def clean(text):
    return text.replace('{', '').replace('}', '').replace('\\&', '&')


def parse_bib(bib_file):
    if not os.path.exists(bib_file):
        raise FileNotFoundError(f"BibTeX file not found: {bib_file}")
    
    parser = bibtex.Parser()
    bib_data = parser.parse_file(bib_file)
    
    publications = []
    for _, entry in bib_data.entries.items():
        if entry.type == 'proceedings':
            authors = [format_author(editor) for editor in entry.persons.get('editor', [])]
            venue = entry.fields.get('publisher', '')
        else:
            authors = [format_author(author) for author in entry.persons.get('author', [])]
            venue = entry.fields.get('journal', '') or entry.fields.get('booktitle', '')

        pub = {
            'title': clean(entry.fields.get('title', '')), # clean_latex_chars
            'authors': authors,
            'journal': clean(venue), # clean_latex_chars
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


if __name__ == '__main__':
    script_dir = Path(__file__).parent
    bib_file = os.path.join(str(script_dir), 'bibliography', 'publications.bib')
    yaml_file = os.path.join(str(script_dir), 'bibliography', 'publications.yaml')
    
    try:
        publications = parse_bib(bib_file)
        with open(yaml_file, 'w') as f:
            f.write(format_yaml_content(publications))
        print(f"Successfully converted {bib_file} to {yaml_file}")
    except FileNotFoundError as e:
        print(f"Error: {e}")