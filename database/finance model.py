from database.db import get_connection

def insert_transaction(user_id, date, t_type, category, amount, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, date, t_type, category, amount, description))
    conn.commit()
    conn.close()

def fetch_transactions(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def set_budget(user_id, limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE user_id=?", (user_id,))
    cursor.execute("INSERT INTO budgets (user_id, monthly_limit) VALUES (?, ?)", (user_id, limit))
    conn.commit()
    conn.close()

def get_budget(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT monthly_limit FROM budgets WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
