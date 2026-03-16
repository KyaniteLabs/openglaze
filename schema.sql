-- OpenGlaze Database Schema
-- SQLite / PostgreSQL compatible

-- Users table (synced with Kratos)
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,  -- Kratos identity ID
    email TEXT UNIQUE NOT NULL,
    studio_name TEXT,
    tier TEXT DEFAULT 'free' CHECK(tier IN ('free', 'pro', 'studio', 'education')),
    template_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Glazes table
CREATE TABLE IF NOT EXISTS glazes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    cone TEXT,
    atmosphere TEXT CHECK(atmosphere IN ('oxidation', 'reduction', 'neutral', 'salt', 'wood')),
    base_type TEXT CHECK(base_type IN ('transparent', 'opaque', 'matte', 'satin', 'gloss')),
    surface TEXT CHECK(surface IN ('smooth', 'textured', 'crystalline', 'runny')),
    color TEXT,
    transparency TEXT CHECK(transparency IN ('transparent', 'semi-opaque', 'opaque')),
    notes TEXT,
    recipe TEXT,  -- JSON array of ingredients
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Ingredients table (for recipe building)
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT CHECK(category IN ('flux', 'stabilizer', 'glassformer', 'colorant', 'opacifier', 'additive')),
    chemical_formula TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Firings table (kiln logs)
CREATE TABLE IF NOT EXISTS firings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    kiln_name TEXT,
    cone_target TEXT,
    atmosphere TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Firing glazes (many-to-many relationship)
CREATE TABLE IF NOT EXISTS firing_glazes (
    firing_id INTEGER NOT NULL,
    glaze_id INTEGER NOT NULL,
    position TEXT,  -- e.g., "top shelf, front"
    notes TEXT,
    result_image_url TEXT,
    PRIMARY KEY (firing_id, glaze_id),
    FOREIGN KEY (firing_id) REFERENCES firings(id) ON DELETE CASCADE,
    FOREIGN KEY (glaze_id) REFERENCES glazes(id) ON DELETE CASCADE
);

-- Subscriptions table (billing)
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    provider_subscription_id TEXT,
    tier TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'canceled', 'past_due', 'pending')),
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_glazes_user_id ON glazes(user_id);
CREATE INDEX IF NOT EXISTS idx_glazes_cone ON glazes(cone);
CREATE INDEX IF NOT EXISTS idx_firings_user_id ON firings(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions(user_id);

-- Insert default ingredients
INSERT OR IGNORE INTO ingredients (name, category) VALUES
    ('Feldspar', 'flux'),
    ('Whiting', 'flux'),
    ('Dolomite', 'flux'),
    ('Talc', 'flux'),
    ('Zinc Oxide', 'flux'),
    ('Silica', 'glassformer'),
    ('Frit 3124', 'glassformer'),
    ('Frit 3134', 'glassformer'),
    ('Kaolin', 'stabilizer'),
    ('Ball Clay', 'stabilizer'),
    ('Bentonite', 'additive'),
    ('Cobalt Carbonate', 'colorant'),
    ('Copper Carbonate', 'colorant'),
    ('Iron Oxide', 'colorant'),
    ('Rutile', 'colorant'),
    ('Tin Oxide', 'opacifier'),
    ('Zircopax', 'opacifier');
