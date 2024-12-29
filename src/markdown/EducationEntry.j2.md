## ((* if entry.degree *))<<entry.degree>> in ((* endif *))<<entry.area>>

- <<entry.institution>>
((* if entry.date_string *))- <<entry.date_string>>
((* endif *))
((* if entry.location *))- <<entry.location>>
((* endif *))
((* for item in entry.highlights *))
- <<item>>
((* endfor *))
