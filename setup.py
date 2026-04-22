import sqlite3

conn = sqlite3.connect('knowledge_base.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS facts (id INTEGER PRIMARY KEY, topic TEXT, fact TEXT)')
c.executemany('INSERT INTO facts (topic, fact) VALUES (?, ?)', [
    ('company', 'LEC AI was founded in 2021 and is based in London'),
    ('product', 'Product X was launched in Q2 2023 with AI-powered features'),
    ('product', 'Product X has over 10,000 active users as of 2024'),
    ('revenue', 'Company revenue grew 45% YoY in 2023'),
    ('team', 'The engineering team has 25 members across London and Lisbon'),
    ('technology', 'The platform uses Python, FastAPI and PostgreSQL in production'),
    ('policy', 'Data retention policy is 90 days for free users, 1 year for paid'),
    ('pricing', 'Basic plan is 29 GBP per month, Pro plan is 99 GBP per month'),
])
conn.commit()
conn.close()
print('Knowledge base created successfully')