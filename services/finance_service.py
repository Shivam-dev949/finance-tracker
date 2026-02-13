import pandas as pd
from database.finance_model import fetch_transactions

def get_user_dataframe(user_id):
    data = fetch_transactions(user_id)
    columns = ["ID","User_ID","Date","Type","Category","Amount","Description"]
    df = pd.DataFrame(data, columns=columns)
    return df

def calculate_summary(df):
    if df.empty:
        return 0,0,0,0

    income = df[df["Type"]=="Income"]["Amount"].sum()
    expense = df[df["Type"]=="Expense"]["Amount"].sum()
    balance = income - expense
    savings_rate = (balance / income * 100) if income > 0 else 0

    return income, expense, balance, savings_rate
