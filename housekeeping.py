import mysql.connector
import pandas as pd
import streamlit as st
from mysql.connector import Error

# Database configuration (update as necessary)
DB_CONFIG = {
    'host': '0.tcp.ap.ngrok.io',  # ngrok host
    'database': 'sql12741294',     # Your database name
    'user': 'root',                # MySQL user
    'password': 'altisBGP@192',    # MySQL password
    'port': 11157                 # ngrok port
}

def fetch_housekeeping_data():
    """Fetch housekeeping booking data."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            query = """
            SELECT b.book_id, b.cot_id, b.check_out_date, s.staff_id, s.staff_name, c.ct_id_stat
            FROM BOOKING b
            JOIN COTTAGE_ATTRIBUTES_RELATION c ON b.cot_id = c.cot_id
            JOIN STAFF s ON b.staff_id = s.staff_id
            WHERE c.ct_id_stat = 3 AND b.payment_status = 2
            """
            df = pd.read_sql(query, connection)
            return df
    except Error as e:
        st.error(f"Error fetching data: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def fetch_full_housekeeping_data():
    """Fetch full data from HOUSEKEEPING table."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            query = "SELECT * FROM HOUSEKEEPING"
            df = pd.read_sql(query, connection)
            return df
    except Error as e:
        st.error(f"Error fetching housekeeping data: {e}")
    finally:
        if connection.is_connected():
            connection.close()

def show_housekeeping():
    """Display housekeeping booking data with payment_status = 2 in Streamlit."""
    df = fetch_housekeeping_data()

    if df is not None and not df.empty:
        st.subheader("Active Bookings")

        # Display the DataFrame including the ct_id_stat column
        st.dataframe(df[['book_id', 'cot_id', 'check_out_date', 'ct_id_stat']])

        # Dropdown for booking ID selection
        selected_book_id = st.selectbox("Select Booking ID", df['book_id'].tolist())

        # Filter staff list for the dropdown
        staff_list = df[['staff_id', 'staff_name']].drop_duplicates()
        staff_dropdown = st.selectbox("Select Staff", staff_list['staff_name'].tolist())

        # Get the selected staff_id
        selected_staff_id = staff_list.loc[staff_list['staff_name'] == staff_dropdown, 'staff_id'].values[0]

        # Convert numpy.int64 to native int for MySQL compatibility
        selected_book_id = int(selected_book_id)
        selected_staff_id = int(selected_staff_id)

        # Assign staff button
        if st.button("Assign Staff"):
            try:
                connection = mysql.connector.connect(**DB_CONFIG)
                if connection.is_connected():
                    cursor = connection.cursor()

                    # Step 1: Update BOOKING with the selected staff_id
                    update_query = """
                    UPDATE BOOKING SET staff_id = %s WHERE book_id = %s
                    """
                    cursor.execute(update_query, (selected_staff_id, selected_book_id))
                    connection.commit()

                    # Step 2: Fetch `cot_id`, `check_out_date`, and the current `ct_id_stat` for the selected booking
                    booking_data_query = """
                    SELECT b.cot_id, b.check_out_date, c.ct_id_stat
                    FROM BOOKING b
                    JOIN COTTAGE_ATTRIBUTES_RELATION c ON b.cot_id = c.cot_id
                    WHERE b.book_id = %s
                    """
                    cursor.execute(booking_data_query, (selected_book_id,))
                    booking_data = cursor.fetchone()
                    cot_id, check_out_date, ct_id_stat = booking_data

                    # Step 3: Insert a new record into HOUSEKEEPING with the fetched `ct_id_stat`
                    insert_housekeeping_query = """
                    INSERT INTO HOUSEKEEPING (book_id, cot_id, check_out_date, ct_id_stat, staff_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_housekeeping_query, (selected_book_id, cot_id, check_out_date, ct_id_stat, selected_staff_id))
                    connection.commit()

                    # Step 3.1: Update ct_id_stat in HOUSEKEEPING table for the newly inserted record
                    update_housekeeping_query = """
                    UPDATE HOUSEKEEPING
                    SET ct_id_stat = 4
                    WHERE book_id = %s AND staff_id = %s AND check_out_date = %s
                    """
                    cursor.execute(update_housekeeping_query, (selected_book_id, selected_staff_id, check_out_date))
                    connection.commit()

                    # Step 4: Update `ct_id_stat` to 4 in COTTAGE_ATTRIBUTES_RELATION for the selected `cot_id`
                    update_ct_id_stat_query = """
                    UPDATE COTTAGE_ATTRIBUTES_RELATION SET ct_id_stat = 4 WHERE cot_id = %s
                    """
                    cursor.execute(update_ct_id_stat_query, (cot_id,))
                    connection.commit()

                    st.success(f"Staff {staff_dropdown} assigned to booking {selected_book_id}, housekeeping record added, and ct_id_stat updated to 4.")
                    st.rerun()
            except Error as e:
                st.error(f"Error updating booking: {e}")
            finally:
                if connection.is_connected():
                    connection.close()
    else:
        st.warning("No bookings available for display.")

    # Always display the full HOUSEKEEPING table and controls
    st.subheader("Full Housekeeping Table")
    housekeeping_df = fetch_full_housekeeping_data()

    # Filter to show only records with ct_id_stat = 4
    filtered_housekeeping_df = housekeeping_df[housekeeping_df['ct_id_stat'] == 4]

    if filtered_housekeeping_df is not None and not filtered_housekeeping_df.empty:
        st.dataframe(filtered_housekeeping_df)

        # Dropdown for selecting housekeep_id from HOUSEKEEPING table
        selected_housekeep_id = st.selectbox("Select Housekeeping ID", filtered_housekeeping_df['housekeep_id'].tolist())

        # Button to mark as complete
        if st.button("Mark As Complete"):
            try:
                connection = mysql.connector.connect(**DB_CONFIG)
                if connection.is_connected():
                    cursor = connection.cursor()

                    # Step 1: Update ct_id_stat to 2 in HOUSEKEEPING for the selected housekeeping record
                    update_housekeeping_query = """
                    UPDATE HOUSEKEEPING
                    SET ct_id_stat = 2
                    WHERE housekeep_id = %s
                    """
                    cursor.execute(update_housekeeping_query, (selected_housekeep_id,))
                    connection.commit()

                    # Step 2: Update ct_id_stat to 2 in COTTAGE_ATTRIBUTES_RELATION for the corresponding cottage
                    update_ct_id_stat_query = """
                    UPDATE COTTAGE_ATTRIBUTES_RELATION
                    SET ct_id_stat = 2
                    WHERE cot_id = (SELECT cot_id FROM HOUSEKEEPING WHERE housekeep_id = %s)
                    """
                    cursor.execute(update_ct_id_stat_query, (selected_housekeep_id,))
                    connection.commit()

                    st.success(f"Housekeeping ID {selected_housekeep_id} marked as complete in both tables.")
                    st.rerun()  # Rerun the app to refresh data
            except Error as e:
                st.error(f"Error marking housekeeping as complete: {e}")
            finally:
                if connection.is_connected():
                    connection.close()



    else:
        st.warning("No housekeeping records available for display.")

# Run the app
if __name__ == "__main__":
    st.title("Housekeeping Management")
    show_housekeeping()
