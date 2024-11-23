import streamlit as st
import mysql.connector
from mysql.connector import Error

# MySQL connection details
host=st.secrets["host"],
port=st.secrets["port"],
user=st.secrets["user"],
password=st.secrets["password"],
database=st.secrets["database"]

def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )


        
        if connection.is_connected():
            st.success("Successfully connected to MySQL!")
            return connection
    except Error as e:
        st.error(f"Error: {e}")
        return None

def fetch_data(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM BOOKING LIMIT 5;")  # Replace with your query
    rows = cursor.fetchall()
    return rows

# Streamlit app layout
st.title("MySQL Connection Test")

# Connect to MySQL
connection = connect_to_mysql()

if connection:
    # Fetch data from MySQL if connection is successful
    data = fetch_data(connection)

    # Display the data in the Streamlit app
    if data:
        st.write("Fetched data from MySQL:")
        st.write(data)

    connection.close()
else:
    st.warning("Unable to connect to MySQL. Please check your connection.")

