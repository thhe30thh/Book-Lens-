PRAGMA foreign_keys = ON;

-- 1. Literary works
CREATE TABLE IF NOT EXISTS works (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    original_title TEXT,
    publication_year INTEGER,
    language TEXT,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Authors
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    birth_year INTEGER,
    death_year INTEGER,
    biography TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        birth_year IS NULL
        OR death_year IS NULL
        OR death_year >= birth_year
    )
);

-- 3. Many-to-many relationship between works and authors
CREATE TABLE IF NOT EXISTS work_authors (
    work_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'author',

    PRIMARY KEY (work_id, author_id, role),

    FOREIGN KEY (work_id)
        REFERENCES works(id) ON DELETE CASCADE,

    FOREIGN KEY (author_id)
        REFERENCES authors(id) ON DELETE CASCADE
);

-- 4. Literary concepts
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (name, category),

    CHECK (category IN (
        'theme',
        'genre',
        'philosophical_idea',
        'literary_movement',
        'historical_period',
        'motif'
    ))
);

-- 5. Connections between works and concepts
CREATE TABLE IF NOT EXISTS work_concepts (
    work_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    relevance INTEGER NOT NULL DEFAULT 3,
    explanation TEXT,

    PRIMARY KEY (work_id, concept_id),

    FOREIGN KEY (work_id)
        REFERENCES works(id) ON DELETE CASCADE,

    FOREIGN KEY (concept_id)
        REFERENCES concepts(id) ON DELETE CASCADE,

    CHECK (relevance BETWEEN 1 AND 5)
);

-- 6. Types of literary relationships
CREATE TABLE IF NOT EXISTS relationship_types (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT
);

-- 7. Relationships between two works
CREATE TABLE IF NOT EXISTS work_relationships (
    id INTEGER PRIMARY KEY,
    source_work_id INTEGER NOT NULL,
    target_work_id INTEGER NOT NULL,
    relationship_type_id INTEGER NOT NULL,
    explanation TEXT NOT NULL,
    confidence REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_work_id)
        REFERENCES works(id) ON DELETE CASCADE,

    FOREIGN KEY (target_work_id)
        REFERENCES works(id) ON DELETE CASCADE,

    FOREIGN KEY (relationship_type_id)
        REFERENCES relationship_types(id),

    UNIQUE (
        source_work_id,
        target_work_id,
        relationship_type_id
    ),

    CHECK (source_work_id != target_work_id),

    CHECK (
        confidence IS NULL
        OR confidence BETWEEN 0.0 AND 1.0
    )
);

-- 8. Sources supporting literary claims
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    url TEXT,
    published_date TEXT,
    source_type TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Sources supporting individual works
CREATE TABLE IF NOT EXISTS work_sources (
    work_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    PRIMARY KEY (work_id, source_id),
    FOREIGN KEY (work_id)
        REFERENCES works(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id)
        REFERENCES sources(id) ON DELETE CASCADE
);

-- 9. Sources supporting work-concept connections
CREATE TABLE IF NOT EXISTS work_concept_sources (
    work_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,

    PRIMARY KEY (work_id, concept_id, source_id),

    FOREIGN KEY (work_id, concept_id)
        REFERENCES work_concepts(work_id, concept_id)
        ON DELETE CASCADE,

    FOREIGN KEY (source_id)
        REFERENCES sources(id) ON DELETE CASCADE
);

-- 10. Sources supporting relationships between works
CREATE TABLE IF NOT EXISTS relationship_sources (
    relationship_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,

    PRIMARY KEY (relationship_id, source_id),

    FOREIGN KEY (relationship_id)
        REFERENCES work_relationships(id) ON DELETE CASCADE,

    FOREIGN KEY (source_id)
        REFERENCES sources(id) ON DELETE CASCADE
);

-- Indexes for frequently queried relationships
CREATE INDEX IF NOT EXISTS idx_work_authors_author
    ON work_authors(author_id);

CREATE INDEX IF NOT EXISTS idx_work_concepts_concept
    ON work_concepts(concept_id);

CREATE INDEX IF NOT EXISTS idx_relationships_source
    ON work_relationships(source_work_id);

CREATE INDEX IF NOT EXISTS idx_relationships_target
    ON work_relationships(target_work_id);

CREATE INDEX IF NOT EXISTS idx_relationships_type
    ON work_relationships(relationship_type_id);

CREATE INDEX IF NOT EXISTS idx_work_sources_source
    ON work_sources(source_id);

CREATE INDEX IF NOT EXISTS idx_sources_url
    ON sources(url);
