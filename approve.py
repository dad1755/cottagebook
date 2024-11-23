import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database configuration (update as necessary)
DB_CONFIG = {
    'host': '0.tcp.ap.ngrok.io',  # ngrok host
    'database': 'sql12741294',     # Your database name
    'user': 'root',                # MySQL user
    'password': 'altisBGP@192',    # MySQL password
    'port': 12691                  # ngrok port
}

# Function to connect to the database and execute queries
def get_database_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return None

# Fetch all booking data with payment_status = 1 (pending)
def fetch_booking_data():
    connection = get_database_connection()
    if connection:
        try:
            query = "SELECT * FROM BOOKING WHERE payment_status = 1"  # Fetch only pending bookings
            booking_data = pd.read_sql(query, connection)
            return booking_data
        except Error as e:
            st.error(f"Error fetching data: {e}")
            return pd.DataFrame()
        finally:
            connection.close()
    return pd.DataFrame()


# Fetch all staff data from the STAFF table
def fetch_staff_data():
    connection = get_database_connection()
    if connection:
        try:
            query = "SELECT staff_id, staff_name FROM STAFF"
            staff_data = pd.read_sql(query, connection)
            return staff_data
        except Error as e:
            st.error(f"Error fetching staff data: {e}")
            return pd.DataFrame()
        finally:
            connection.close()
    return pd.DataFrame()

# Function to update payment_status and assign staff_id for a specific booking
def confirm_booking(book_id, staff_id):
    connection = get_database_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Update payment_status to 2 and assign staff_id for the selected booking
            update_query = """
                UPDATE BOOKING
                SET payment_status = 2, staff_id = %s
                WHERE book_id = %s
            """
            cursor.execute(update_query, (staff_id, book_id))
            connection.commit()

            # Get cot_id for the confirmed booking
            cot_query = "SELECT cot_id FROM BOOKING WHERE book_id = %s"
            cursor.execute(cot_query, (book_id,))
            cot_id_result = cursor.fetchone()
            if cot_id_result:
                cot_id = cot_id_result[0]  # Fetch cot_id of the current booking

                # Delete other bookings with the same cot_id and payment_status = 1
                delete_query = "DELETE FROM BOOKING WHERE cot_id = %s AND payment_status = 1 AND book_id != %s"
                cursor.execute(delete_query, (cot_id, book_id))
                connection.commit()

                # Update ct_id_stat to 3 in COTTAGE_ATTRIBUTES_RELATION
                update_cottage_query = "UPDATE COTTAGE_ATTRIBUTES_RELATION SET ct_id_stat = 3 WHERE cot_id = %s"
                cursor.execute(update_cottage_query, (cot_id,))
                connection.commit()

                st.success(f"Booking ID {book_id} has been confirmed! Staff ID {staff_id} has been assigned.")
                st.rerun()  # Refresh the app

        except Error as e:
            st.error(f"Error updating booking: {e}")
        finally:
            if cursor:
                cursor.close()
            connection.close()


# Streamlit UI for displaying and managing booking confirmation
def show_approve_management():
    st.subheader("Booking Management")
    st.write("All Bookings (Pending and Confirmed)")

    # Fetch and display booking data
    booking_data = fetch_booking_data()
    if not booking_data.empty:
        # Display booking data in a table
        st.dataframe(booking_data)

        # Dropdown to select a booking ID
        book_id_list = booking_data['book_id'].tolist()
        selected_book_id = st.selectbox("Select Booking ID to Confirm", book_id_list)

        # Fetch the selected booking's current status
        selected_booking = booking_data[booking_data['book_id'] == selected_book_id]
        if not selected_booking.empty:
            current_status = selected_booking.iloc[0]['payment_status']
            if current_status == 2:
                st.info(f"Booking ID {selected_book_id} is already confirmed.")
            else:
                # Fetch staff data and create dropdown for staff selection
                staff_data = fetch_staff_data()
                if not staff_data.empty:
                    staff_options = staff_data['staff_name'] + " (ID: " + staff_data['staff_id'].astype(str) + ")"
                    selected_staff = st.selectbox("Select Staff to Confirm Booking", staff_options)
                    selected_staff_id = int(selected_staff.split(" (ID: ")[1][:-1])  # Extract staff_id from the selected option

                    # Confirm button
                    if st.button("CONFIRM"):
                        confirm_booking(selected_book_id, selected_staff_id)
                else:
                    st.write("No staff available for assignment.")
    else:
        st.write("No bookings available.")

# Run this function only if this script is executed directly
if __name__ == "__main__":
    show_approve_management()
