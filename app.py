import streamlit as st
import pandas as pd
from datetime import datetime


st.set_page_config(page_title="Mobile Sales Tracker", layout="wide")
st.write("## In the name of God, the Most Gracious, the Most Merciful")

DATA_FILE = "sales_data.csv"

def load_data():
    try:
        return pd.read_csv(DATA_FILE).to_dict(orient='records')
    except FileNotFoundError:
        return []

def save_data():
    df = pd.DataFrame(st.session_state.data)
    df.to_csv(DATA_FILE, index=False)

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'data' not in st.session_state:
    st.session_state.data = load_data()

VALID_USERNAME = "kaka"
VALID_PASSWORD = "#azmatufo"
PASSKEY = "aujac"

def authenticate(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

def login_form():
    with st.form("Login"):
        st.write("## 🔒 Login to Access System")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

if not st.session_state.logged_in:
    login_form()
    st.stop()

def ensure_paid_key():
    for entry in st.session_state.data:
        if "Paid" not in entry:
            entry["Paid"] = 0

def add_entry(date, holder_name, mobile_name, mobile_rate, paid):
    remaining_amount = max(0, mobile_rate - paid)  # Adjust remaining amount
    new_entry = {
        "Date": date,
        "Holder Name": holder_name,
        "Mobile Name": mobile_name,
        "Mobile Rate": mobile_rate,
        "Remaining Amount": remaining_amount,
        "Paid": paid
    }
    st.session_state.data.append(new_entry)
    save_data()

def update_remaining_amount(index, amount_paid):
    if amount_paid <= st.session_state.data[index]["Remaining Amount"]:
        st.session_state.data[index]["Remaining Amount"] -= amount_paid
        st.session_state.data[index]["Paid"] += amount_paid
        st.success(f"₹{amount_paid} paid for {st.session_state.data[index]['Holder Name']}!")
        save_data()
    else:
        st.error("Amount paid cannot exceed the remaining amount!")

def calculate_summary():
    ensure_paid_key()
    total_sold = len(st.session_state.data)
    total_remaining = sum(entry["Remaining Amount"] for entry in st.session_state.data)
    total_collected = sum(entry["Paid"] for entry in st.session_state.data)
    return total_sold, total_remaining, total_collected

def clear_data():
    st.session_state.data = []
    save_data()
    st.success("All data cleared successfully!")

def remove_entry(index):
    del st.session_state.data[index]
    save_data()
    st.success("Entry removed successfully!")
    st.experimental_rerun()

with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

st.title("📱 Mobile Sales DATA")

st.write("DBS")
total_sold, total_remaining, total_collected = calculate_summary()
col1, col2, col3 = st.columns(3)
col1.metric("📦 New Mobiles Sold", total_sold)
col2.metric("💰 Total Remaining Cash", f"₹{total_remaining}")
col3.metric("💵 Total Cash Collected", f"₹{total_collected}")

with st.expander("📝 Add New Mobile Sale", expanded=True):
    with st.form("entry_form"):
        date = st.date_input("Date", datetime.today())
        holder_name = st.text_input("Holder Name")
        mobile_name = st.text_input("Mobile Name")
        mobile_rate = st.number_input("Mobile Rate (₹)", min_value=0)
        paid = st.number_input("Paid (₹)", min_value=0)
        passkey = st.text_input("Enter Passkey to Add New Mobile", type="password")
        
        submitted = st.form_submit_button("💾 Save as Voucher")
        if submitted:
            if passkey == PASSKEY:
                add_entry(date, holder_name, mobile_name, mobile_rate, paid)
                st.success("Voucher saved successfully!")
            else:
                st.error("Incorrect passkey! Access denied.")
    
    if st.button("🧹 Clear All Data"):
        if st.session_state.data:
            st.warning("Are you sure you want to clear all data? This action cannot be undone.")
            if st.button("✅ Confirm Clear Data"):
                clear_data()
                st.experimental_rerun()
        else:
            st.info("No data to clear.")

st.write("### 📜 Existing Entries")
if st.session_state.data:
    ensure_paid_key()
    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)
    
    for i, entry in enumerate(st.session_state.data):
        with st.expander(f"🗂 {entry['Holder Name']} - {entry['Mobile Name']}"):
            st.write(f"**Date:** {entry['Date']}")
            st.write(f"**Mobile Rate:** ₹{entry['Mobile Rate']}")
            st.write(f"**Remaining Amount:** ₹{entry['Remaining Amount']}")
            st.write(f"**Paid:** ₹{entry['Paid']}")
            if st.button("❌ Remove Entry", key=f"remove_{i}"):
                remove_entry(i)
    
    with st.sidebar:
        st.write("### 💵 Add Cash Collection")
        holder_names = [entry["Holder Name"] for entry in st.session_state.data]
        selected_holder = st.selectbox("Select Holder Name", holder_names)
        selected_index = next(i for i, entry in enumerate(st.session_state.data) if entry["Holder Name"] == selected_holder)
        
        st.write(f"**Mobile Name:** {st.session_state.data[selected_index]['Mobile Name']}")
        st.write(f"**Remaining Amount:** ₹{st.session_state.data[selected_index]['Remaining Amount']}")
        st.write(f"**Paid:** ₹{st.session_state.data[selected_index]['Paid']}")
        
        with st.form("cash_form"):
            amount_paid = st.number_input("Amount Paid (₹)", min_value=0)
            passkey = st.text_input("Enter Passkey to Add Cash", type="password")
            submitted = st.form_submit_button("💸 Add Cash")
            if submitted:
                if passkey == PASSKEY:
                    update_remaining_amount(selected_index, amount_paid)
                    st.experimental_rerun()
                else:
                    st.error("Incorrect passkey! Access denied.")
else:
    st.info("No entries yet. Add a new mobile sale to get started!")
