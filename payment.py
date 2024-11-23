import streamlit as st
import mysql.connector
from mysql.connector import Error

# Database configuration (update as necessary)
DB_CONFIG = {
    'host': '0.tcp.ap.ngrok.io',  # ngrok host
    'database': 'sql12741294',     # Your database name
    'user': 'root',                # MySQL user
    'password': 'altisBGP@192',    # MySQL password
    'port': 11157                 # ngrok port
}
def execute_query(query, params=None):
    """Execute a query with optional parameters."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(query, params if params else ())
        connection.commit()
    except Error as e:
        st.error(f"Database Error: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def fetch_data(query, params=None):
    """Fetch data from the database and return it as a list of dictionaries."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params if params else ())
        return cursor.fetchall()
    except Error as e:
        st.error(f"Database Error: {e}")
        return []
    finally:
        if connection:
            cursor.close()
            connection.close()

# Generic CRUD Functions
def create_record(table, column, value):
    """Add a new record to the specified table."""
    query = f"INSERT INTO {table} ({column}) VALUES (%s)"
    execute_query(query, (value,))

def delete_record(table, id_column, record_id):
    """Delete a record from the specified table by ID."""
    query = f"DELETE FROM {table} WHERE {id_column} = %s"
    execute_query(query, (record_id,))

def get_records(table):
    """Retrieve all records from the specified table."""
    query = f"SELECT * FROM {table}"
    return fetch_data(query)

# Streamlit UI for Payment Management
def show_payment_management():
    st.subheader("Payment Management")

    # Payment Types Management
    st.write("###### This Function To Add New Payment Types 💻")
    payment_type_details = st.text_input("Enter Name For New Payment Type", key="payment_type_input_80")  # Unique key
    if st.button("Confirm Add New Payment Type", key="add_payment_type_button_81"):  # Unique key
        if payment_type_details:
            create_record("PAYMENT_TYPES", "pt_details", payment_type_details)
            st.success(f"Added Payment Type: {payment_type_details}")
            payment_type_details = ""  # Clear input after success
        else:
            st.warning("Please enter Payment Type Details.")

    st.write("###### Available Payment Type in Database")
    payment_types_data = get_records("PAYMENT_TYPES")
    if payment_types_data:
        st.dataframe(payment_types_data)
        pt_id_to_delete = st.text_input("Enter Payment Type ID to delete", key="pt_id_to_delete_82")  # Unique key
        if st.button("Confirm Delete Payment Type", key="delete_payment_type_button_83"):  # Unique key
            if pt_id_to_delete.isdigit():
                delete_record("PAYMENT_TYPES", "pt_id", int(pt_id_to_delete))
                st.success(f"Deleted Payment Type with ID: {pt_id_to_delete}")
            else:
                st.warning("Please enter a valid numeric Payment Type ID to delete.")
    else:
        st.warning("No payment types found. Consider adding one.")

    # Payment Status Management
    st.write("###### This Function To Add New Payment Status")
    payment_status_details = st.text_input("Enter Name For New Payment Status", key="payment_status_input_84")  # Unique key
    if st.button("Confirm Add New Payment Status", key="add_payment_status_button_85"):  # Unique key
        if payment_status_details:
            create_record("PAYMENT_STATUS", "pay_details", payment_status_details)
            st.success(f"Added Payment Status: {payment_status_details}")
            payment_status_details = ""  # Clear input after success
        else:
            st.warning("Please enter Payment Status Details.")

    st.write("###### Available Payment Statuses in Database")
    payment_status_data = get_records("PAYMENT_STATUS")
    if payment_status_data:
        st.dataframe(payment_status_data)
        pay_id_to_delete = st.text_input("Enter Payment Status ID to delete", key="pay_id_to_delete_86")  # Unique key
        if st.button("Delete Payment Status", key="delete_payment_status_button_87"):  # Unique key
            if pay_id_to_delete.isdigit():
                delete_record("PAYMENT_STATUS", "pay_id", int(pay_id_to_delete))
                st.success(f"Deleted Payment Status with ID: {pay_id_to_delete}")
            else:
                st.warning("Please enter a valid numeric Payment Status ID to delete.")
    else:
        st.warning("No payment statuses found. Consider adding one.")

# Run the payment management function to show the UI

# Run the application
if __name__ == "__main__":
    show_payment_management()
