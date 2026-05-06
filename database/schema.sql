-- Rulexo enquiry system schema
-- Lead sources: bark, facebook, website, checkatrade

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    trade_type TEXT,
    email TEXT,
    phone TEXT,
    voice_profile TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    source TEXT,          -- bark | facebook | website | checkatrade
    name TEXT,
    phone TEXT,
    email TEXT,
    business_type TEXT,
    pain_point TEXT,
    message TEXT,
    budget TEXT,
    timeframe TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'new',
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS qualifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    score INTEGER,
    decision TEXT,
    reason TEXT,
    qualified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    direction TEXT,
    channel TEXT,
    sender TEXT,
    message_content TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent',
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    channel TEXT,
    recipient_type TEXT,
    recipient_contact TEXT,
    message_content TEXT,
    generated_by TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'sent',
    FOREIGN KEY (lead_id) REFERENCES leads(id),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);
