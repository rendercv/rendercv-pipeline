from pybtex.database.input import bibtex
from pybtex.database.output import bibtex as bibtex_writer
import os
from pathlib import Path
import requests


def convert_latex_diacritics(text):
    replacements = [
        ("{\\&}", "&"),
        ('{\\"{a}}', "ä"),
        ("{\\~{a}}", "ã"),  # {\~{a}} Guimar{\~{a}}es
        ("{\\~\\{a\\}}", "ã"),  # For {\~{a}}
        ("\\~{a}", "ã"),  # Another variation
        ("\\'o", "ó"),
        ("\\'i", "í"),
        ("\\'a", "á"),
        ("{\\'o}", "ó"),
        ("{\\'{o}}", "ó"),  # {\'{o}}
        ("{\\'i}", "í"),
        ("{\\'{\\i}}", "í"),  # {\'{\i}}
        ("{\\'a}", "á"),
        ('{\\"u}', "ü"),
        ('{\\"o}', "ö"),
        ('{\\"O}', "Ö"),
        ('{\\"{u}}', "ü"),
        ('{\\"{o}}', "ö"),
        ('{\\"{O}}', "Ö"),
        ('{"O}', "Ö"),
        ("{\\c{c}}", "ç"),
        ("{\\`{e}}", "è"),  # {\`{e}}
        ("{\\ae}", "æ"),  # {\ae}
        ("{-}", "-"),
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
    parts = name.split("-")
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
    last_block = " ".join(convert_latex_diacritics(ln) for ln in author.last_names)

    full_name = f"{initial_block} {last_block}".strip()

    # Special case for F. Calefato
    if full_name.lower() == "f. calefato":
        return f'"***{full_name}***"'
    return full_name


def clean_latex_markup(text):
    return text.replace("{", "").replace("}", "")


def filter_bib(bib_file):
    class NoEscapeWriter(bibtex_writer.Writer):
        def _encode(self, text):
            return text

    # load bib file
    parser = bibtex.Parser()
    bib_data = parser.parse_file(bib_file)

    # filter out entries where publisher is '{Zenodo}' or journal is '{CoRR}' or key is 'DBLP:conf/icgse/2019'
    filtered_entries = {
        key: entry
        for key, entry in bib_data.entries.items()
        if entry.fields.get("publisher", "").strip("{}") != "Zenodo"
        and entry.fields.get("journal", "").strip("{}") != "CoRR"
        and key != "DBLP:conf/icgse/2019"
    }

    # Update bib_data with filtered entries
    bib_data.entries = filtered_entries

    # sort entries by year in descending order
    bib_data.entries = dict(
        sorted(
            bib_data.entries.items(),
            key=lambda x: x[1].fields.get("year", ""),
            reverse=True,
        )
    )

    # write filtered entries back to bib file
    writer = NoEscapeWriter()
    with open(bib_file, "w") as f:
        writer.write_file(bib_data, f)


def parse_bib(bib_file):
    if not os.path.exists(bib_file):
        raise FileNotFoundError(f"BibTeX file not found: {bib_file}")

    parser = bibtex.Parser()
    bib_data = parser.parse_file(bib_file)

    publications = []
    for _, entry in bib_data.entries.items():
        if entry.type == "proceedings":
            authors = [
                format_author(editor) for editor in entry.persons.get("editor", [])
            ]
            venue = entry.fields.get("publisher", "")
            title = entry.fields.get("title", "")
        elif entry.type == "inbook":
            authors = [
                format_author(author) for author in entry.persons.get("author", [])
            ]
            venue = entry.fields.get("title", "")
            title = entry.fields.get("chapter", "")
        else:
            authors = [
                format_author(author) for author in entry.persons.get("author", [])
            ]
            venue = entry.fields.get("journal", "") or entry.fields.get("booktitle", "")
            title = entry.fields.get("title", "")

        rank = entry.fields.get("ranking", "")
        pub = {
            "title": clean_latex_markup(convert_latex_diacritics(title)),
            "authors": authors,
            "journal": clean_latex_markup(convert_latex_diacritics(venue)),
            "doi": entry.fields.get("doi", "").replace("\\_", "_"),
            "rank": rank,
        }

        if "year" in entry.fields:
            pub["date"] = entry.fields["year"]

        if "volume" in entry.fields:
            pub["journal"] += f", vol. {entry.fields['volume']}"
        if "number" in entry.fields:
            pub["journal"] += f", no. {entry.fields['number']}"
        pub["journal"] = clean_latex_markup(pub["journal"])

        publications.append(pub)

    # sort by year in descending order
    publications.sort(key=lambda x: x["date"], reverse=True)
    return {"publications": publications}


def format_yaml_content(data, section="publications"):
    output = f"    {section}:\n"
    for pub in data["publications"]:
        output += f"      - title: \"{pub['title']}\"\n"
        output += "        authors:\n"
        for author in pub["authors"]:
            output += f"          - {author}\n"
        output += f"        date: {pub['date']}\n"
        output += f"        journal: \"{pub['journal']}\"\n"
        if pub.get("doi"):
            output += f"        doi: {pub['doi']}\n"
        if pub.get("rank"):
            output += f"        rank: {pub['rank']}\n"
    return output


def download_bib_from_dblp(file, url):
    try:
        response = requests.get(url, timeout=10)  # 10 second timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses

        with open(os.path.join(file), "wb") as f:
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
    with open(dblp_file, "r") as f:
        dblp_content = f.read()
    with open(additional_file, "r") as f:
        additional_content = f.read()

    with open(output_file, "w") as f:
        f.write(dblp_content)
        f.write("\n\n")
        f.write(additional_content)


if __name__ == "__main__":
    # author's DBLP URL
    dblp_url = "https://dblp.org/pid/48/5662.bib?param=1"

    script_dir = Path(__file__).parent
    dblp_file = os.path.join(str(script_dir), "bibliography", "dblp.bib")
    additional_entries = os.path.join(
        str(script_dir), "bibliography", "not_in_dblp.bib"
    )
    all_pubblications_bib_file = os.path.join(
        str(script_dir), "bibliography", "publications.bib"
    )
    selected_pubblications_bib_file = os.path.join(
        str(script_dir), "bibliography", "selected.bib"
    )
    all_pubblications_yaml_file = os.path.join(
        str(script_dir), "bibliography", "publications.yaml"
    )
    selected_pubblications_yaml_file = os.path.join(
        str(script_dir), "bibliography", "selected_publications.yaml"
    )

    try:
        download_bib_from_dblp(dblp_file, dblp_url)
        merge_bib_files(dblp_file, additional_entries, all_pubblications_bib_file)
        filter_bib(all_pubblications_bib_file)
        all_publications = parse_bib(all_pubblications_bib_file)
        with open(all_pubblications_yaml_file, "w") as f:
            f.write(format_yaml_content(all_publications, section="publications"))
        selected_publications = parse_bib(selected_pubblications_bib_file)
        with open(selected_pubblications_yaml_file, "w") as f:
            f.write(
                format_yaml_content(
                    selected_publications, section="selected_publications"
                )
            )
    except FileNotFoundError as e:
        print(f"Error: {e}")
