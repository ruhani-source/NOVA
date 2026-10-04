-- NOVA: persistent new information.
-- database_service.init_database() creates this automatically on first use.
-- Run it manually in the Supabase SQL editor only if you prefer.

CREATE TABLE IF NOT EXISTS nova_information (
    id          SERIAL PRIMARY KEY,
    information TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keep the table private to the backend: no RLS policies means Supabase's
-- public Data API (anon key) cannot read or write it. The backend connects
-- as the table owner through DATABASE_URL, which RLS does not restrict.
ALTER TABLE nova_information ENABLE ROW LEVEL SECURITY;
