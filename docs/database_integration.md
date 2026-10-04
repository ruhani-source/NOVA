# Database integration (for `backend/routes.py`)

`backend/services/database_service.py` replaces the in-memory
`new_information = []` list with persistent storage in Supabase/PostgreSQL.
Routes never touch SQL.

## Setup

Add to `.env` (never commit it):

```
DATABASE_URL=postgresql://...   # Supabase connection string (URI)
```

The `nova_information` table is created automatically on first use
(schema: `docs/database_schema.sql`). If `DATABASE_URL` is missing or
Supabase is unreachable, information is saved to
`data/new_information_fallback.json` instead, and `get_information()`
returns database + fallback items together. The demo keeps working.

## Changes in `backend/routes.py`

Import the module, not the functions: the GET route is already named
`get_information`, so a bare import would be shadowed.

```python
from backend.services import database_service
```

Delete `new_information = []`, then:

**POST /information** — replace `new_information.append(information)` with:

```python
database_service.save_information(information)
```

**GET /information** — replace `new_information` with:

```python
return jsonify({
    "information": database_service.get_information()
})
```

**POST /ask** — replace `information = new_information` with:

```python
information = database_service.get_information()
```

`answer_question(question, information)` is unchanged.

### Optional: timestamp-aware answers

Instead of the two lines above in `/ask`, call:

```python
from backend.services.ask_nova import answer_question_with_database

answer = answer_question_with_database(question)
```

It passes each item as `[added <timestamp>] <text>`, so Gemini can tell
which information is newest.

## API reference

| Function | Returns |
|---|---|
| `save_information(text)` | saved record dict; raises `ValueError` on empty text |
| `get_information()` | `list[str]`, oldest first |
| `get_information_records()` | `list[dict]` with `id`, `information`, `created_at`, `storage` |
| `is_database_available()` | `True` if Supabase is reachable |

## Tests

```
python -m unittest tests.test_database_service -v
```

The live Supabase test runs only when `DATABASE_URL` is set.
