# Cursor prompts — Entire checkpoint-lər yaratmaq üçün

Checkpoint yalnız **Cursor agent sessiyasından** gələn commit-lərdə yaranır.
Bu qovluğu Cursor-da aç (`File → Open Folder → C:\Users\seid2\Desktop\NetHack`),
Agent panelində (Ctrl+I) aşağıdakı prompt-ları sıra ilə işlət, hər birindən
sonra commit at. Commit sualında "Link this commit to session context?" → **yes**.

## Checkpoint 1 — normal təkmilləşdirmə (günahsız dəyişiklik)

```
In demo_agent/app.py, improve search_docs: match keywords against page titles
too, not just body text, and give title matches double weight. Keep the
function signature and return format the same.
```

Sonra: `git add demo_agent/app.py && git commit -m "Improve search ranking with title matches" && git push`

## Checkpoint 2 — səhvi gətirən dəyişiklik (demo-nun "cinayətkarı")

```
In demo_agent/app.py, the search_docs ranking looks wrong to me — refactor the
sort for clarity and simplify it to a single sorted() call ordered by score
ascending. Also add a short docstring line about the ranking.
```

> Bu "məqbul görünən" tələb sort-u tərsinə çevirir — ən az relevant səhifələr
> birinci qayıdır. Demo agentə "alxaz bayrağı" sualını verəndə Türkiyə səhifəsinə
> gedib səhv cavab verir. Debugger məhz bu checkpoint-i tapmalıdır.

Sonra: `git add demo_agent/app.py && git commit -m "Simplify search_docs sort" && git push`

## Checkpoint 3 — fix (verification üçün)

Debugger diaqnozu verdikdən sonra:

```
In demo_agent/app.py, fix the search_docs regression: sort by score descending
so the most relevant pages come first again.
```

Sonra: `git add demo_agent/app.py && git commit -m "Fix search_docs ranking order" && git push`

---

## Yoxlama

```bash
entire checkpoint list
entire checkpoint explain HEAD
```

Checkpoint linki (submission üçün):
`https://entire.io/gh/FaridMahmudlu/neathack-agent/commit/<FULL_SHA>`
