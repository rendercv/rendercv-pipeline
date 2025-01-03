## <<entry.title>> ((* if entry.date_string *)) (<<entry.date_string>>) ((* endif *))

- <<entry.authors|join(", ")>>
((* if entry.journal *))
- <<entry.journal>>((* if entry.doi *)), doi:[<<entry.doi>>](<<entry.doi_url>>)((* elif entry.url *))[<<entry.url>>](<<entry.clean_url|escape_latex_characters>>)((* endif *)) 
((* if entry.rank *))
- Rank: <<entry.rank>>
((* endif *))
((* endif *))
