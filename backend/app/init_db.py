from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://admin:admin123@localhost:5432/bi_recommendation"

engine = create_engine(DATABASE_URL)

create_table_query = """
CREATE TABLE IF NOT EXISTS user_logs (
    id SERIAL PRIMARY KEY,
    user_id INT,
    report_name VARCHAR(255),
    action VARCHAR(50),
    duration INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

with engine.connect() as conn:
    conn.execute(text(create_table_query))
    conn.commit()

print("Table created successfully")