import os
import re

def fix_index_html():
    source_file = os.path.join(os.path.dirname(__file__), "..", "docs", "index.html")
    with open(source_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(source_file, "w", encoding="utf-8") as f:
        for line in lines:
            # Replace ' in</h2>' at the end of the line with '  </h2>'
            fixed_line = re.sub(r" in</h2>$", "</h2>", line)
            f.write(fixed_line)

if __name__ == "__main__":
    fix_index_html()