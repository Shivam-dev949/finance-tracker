import streamlit as st
import pandas as pd
import hashlib
import streamlit as st

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- SESSION STATE ---------------- #
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# ---------------- THEME FUNCTION ---------------- #
def apply_theme(theme):
    if theme == "Dark":
        st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                color: white;
            }
            .block-container {
                padding: 2rem 3rem;
            }
            .card {
                background: rgba(255, 255, 255, 0.05);
                padding: 20px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #ffffff, #f0f2f6);
                color: black;
            }
            .block-container {
                padding: 2rem 3rem;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("⚙ Settings")
theme_choice = st.sidebar.toggle("🌙 Dark Mode")

if theme_choice:
    st.session_state.theme = "Dark"
else:
    st.session_state.theme = "Light"

apply_theme(st.session_state.theme)

from database.db import initialize_database, get_connection

# ---------------- INITIALIZE DB ---------------- #
initialize_database()

st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.login-box {
    background-color: #1C1F26;
    padding: 40px;
    border-radius: 15px;
    box-shadow: 0px 0px 25px rgba(99,102,241,0.3);
}
.stButton>button {
    background-color: #6366F1;
    color: white;
    border-radius: 8px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ---------------- #

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?,?)",
                       (username, hash_password(password)))
        conn.commit()
        st.success("Registered Successfully!")
    except:
        st.error("Username already exists!")
    conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def add_transaction(user_id, date, t_type, category, amount, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, date, type, category, amount, description)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, str(date), t_type, category, amount, description))
    conn.commit()
    conn.close()

def get_transactions(user_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC",
        conn,
        params=(user_id,)
    )
    conn.close()
    return df

# ---------------- SESSION ---------------- #

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- LOGIN PAGE ---------------- #

if st.session_state.user is None:
    st.markdown("<h1 style='text-align:center;'>💰 Personal Finance Tracker</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        option = st.selectbox("Choose Option", ["Login", "Register"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if option == "Register":
            if st.button("Register"):
                register_user(username, password)

        if option == "Login":
            if st.button("Login"):
                user = login_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MAIN APP ---------------- #

else:
    user_id = st.session_state.user[0]

    # Sidebar
    st.sidebar.markdown("## 💰 Finance Tracker")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio("Navigation",
                            ["Dashboard", "Add Transaction", "Transactions", "Logout"])

    if menu == "Logout":
        st.session_state.user = None
        st.rerun()

    df = get_transactions(user_id)

    # ---------------- DASHBOARD ---------------- #

    if menu == "Dashboard":
        st.title("📊 Dashboard")

        if not df.empty:
            income = df[df["type"]=="Income"]["amount"].sum()
            expense = df[df["type"]=="Expense"]["amount"].sum()
            balance = income - expense
            savings_rate = (balance/income*100) if income>0 else 0

            st.markdown("## 💼 Financial Overview")

            col1,col2,col3,col4 = st.columns(4)

            col1.markdown(f"""
            <div style="background:#1C1F26;padding:20px;border-radius:15px;">
            <h4>Income</h4>
            <h2 style="color:#22c55e;">₹{income}</h2>
            </div>
            """, unsafe_allow_html=True)

            col2.markdown(f"""
            <div style="background:#1C1F26;padding:20px;border-radius:15px;">
            <h4>Expense</h4>
            <h2 style="color:#ef4444;">₹{expense}</h2>
            </div>
            """, unsafe_allow_html=True)

            col3.markdown(f"""
            <div style="background:#1C1F26;padding:20px;border-radius:15px;">
            <h4>Balance</h4>
            <h2 style="color:#6366F1;">₹{balance}</h2>
            </div>
            """, unsafe_allow_html=True)

            col4.markdown(f"""
            <div style="background:#1C1F26;padding:20px;border-radius:15px;">
            <h4>Savings %</h4>
            <h2>{savings_rate:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📈 Expense by Category")
            exp_df = df[df["type"]=="Expense"]
            if not exp_df.empty:
                st.bar_chart(exp_df.groupby("category")["amount"].sum())

        else:
            st.info("No transactions yet.")

    # ---------------- ADD TRANSACTION ---------------- #

    if menu == "Add Transaction":
        st.title("➕ Add Transaction")

        date = st.date_input("Date")
        t_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0)
        desc = st.text_area("Description")

        if st.button("Add"):
            add_transaction(user_id, date, t_type, category, amount, desc)
            st.success("Transaction Added Successfully!")

    # ---------------- TRANSACTIONS ---------------- #

    if menu == "Transactions":
        st.title("📂 Transactions")

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])

            start = st.date_input("From", df["date"].min())
            end = st.date_input("To", df["date"].max())

            filtered = df[(df["date"]>=pd.to_datetime(start)) &
                          (df["date"]<=pd.to_datetime(end))]

            st.dataframe(filtered, use_container_width=True)

            csv = filtered.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, "transactions.csv")
        else:
            st.info("No transactions found.")


