import os
import re


def fix_index_html():
    source_file = os.path.join(
        os.path.dirname(__file__), "..", "Fabio_Calefato_CV.html"
    )
    output_file = os.path.join(os.path.dirname(__file__), "..", "docs", "index.md")
    with open(source_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            # Remove '<!DOCTYPE html>' at the beginning of the file
            fixed_line = re.sub(r"^<!DOCTYPE html>\n", "", line)
            # Replace ' in</h2>' at the end of the line with '  </h2>'
            fixed_line = re.sub(r" in</h2>$", "</h2>", fixed_line)
            # Replace "``"" with "''"
            fixed_line = re.sub(r"``", "''", fixed_line)
            f.write(fixed_line)


def replace_css_links():
    source_file = os.path.join(os.path.dirname(__file__), "..", "docs", "index.md")
    # replace old with new style string
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()
    """Remove external CSS links with local stylesheet reference"""
    css_pattern1 = r'<link rel="stylesheet".*?/>'
    updated_content = re.sub(css_pattern1, "", content, flags=re.DOTALL)
    css_pattern2 = r'<link rel="stylesheet" href="https://.*?/?>'
    updated_content = re.sub(css_pattern2, "", updated_content, flags=re.DOTALL)
    # write updated content to file
    with open(source_file, "w", encoding="utf-8") as f:
        f.write(updated_content)


if __name__ == "__main__":
    fix_index_html()
    replace_css_links()
