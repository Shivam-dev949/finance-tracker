import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# ---------------- THEME SYSTEM ---------------- #

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True


def apply_theme():
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: white;
        }
        section[data-testid="stSidebar"] {
            background-color: #111827;
        }
        .stButton>button {
            background: linear-gradient(45deg, #6366F1, #8B5CF6);
            color: white;
            border-radius: 12px;
            height: 3em;
            width: 100%;
            border: none;
        }
        .stTextInput input, .stSelectbox div {
            background-color: #1f2937;
            color: white;
            border-radius: 8px;
        }
        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #ffffff, #e3f2fd);
            color: black;
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        .stButton>button {
            background: linear-gradient(45deg, #6366F1, #8B5CF6);
            color: white;
            border-radius: 12px;
            height: 3em;
            width: 100%;
            border: none;
        }
        </style>
        """, unsafe_allow_html=True)


apply_theme()

# ---------------- DATABASE ---------------- #

def get_connection():
    return sqlite3.connect("finance.db")


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        type TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()


initialize_database()

# ---------------- HELPER ---------------- #

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        st.success("Registered Successfully!")
    except:
        st.error("Username already exists!")
    conn.close()


def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return user


# ---------------- SESSION ---------------- #

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- SIDEBAR SETTINGS ---------------- #

st.sidebar.title("⚙ Settings")

dark_toggle = st.sidebar.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)

if dark_toggle != st.session_state.dark_mode:
    st.session_state.dark_mode = dark_toggle
    st.rerun()

# ---------------- LOGIN PAGE ---------------- #

if st.session_state.user is None:

    st.markdown("<h1 style='text-align:center;'>💰 Personal Finance Tracker</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
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

# ---------------- AFTER LOGIN ---------------- #

else:
    st.success(f"Welcome {st.session_state.user[1]} 👋")
    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

