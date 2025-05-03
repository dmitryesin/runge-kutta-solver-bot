create Table users (
    id INT PRIMARY KEY NOT NULL,
    language VARCHAR(2) NOT NULL,
    rounding VARCHAR(2) NOT NULL,
    method VARCHAR(25) NOT NULL
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    parameters JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('new', 'in_progress', 'completed', 'error')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);