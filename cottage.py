import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database configuration
DB_CONFIG = {
    'host': '0.tcp.ap.ngrok.io',  # ngrok host
    'database': 'sql12741294',     # Your database name
    'user': 'root',                # MySQL user
    'password': 'altisBGP@192',    # MySQL password
    'port': 11157                  # ngrok port
}

def create_connection():
    """Create a database connection using a context manager."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        st.error(f"The error '{e}' occurred")
        return None

def fetch_all_data():
    """Fetch data from all related tables."""
    connection = create_connection()
    if connection is None:
        return None

    tables = [
        'COTTAGE', 'POOL', 'LOCATION', 'ROOM', 'MAXIMUM_PAX', 'COTTAGE_TYPES',
        'COTTAGE_STATUS', 'COTTAGE_ATTRIBUTES_RELATION', 'COTTAGE_TOILET',
        'COTTAGE_BALCONY', 'COTTAGE_STOREY', 'AIRCOND_ROOM',
        'KITCHEN_TYPES', 'PARKING_TYPES'
    ]
    data = {}
    try:
        for table in tables:
            query = f"SELECT * FROM {table}"
            df = pd.read_sql(query, connection)
            data[table] = df
    except Error as e:
        st.error(f"Failed to fetch data: {e}")
    finally:
        connection.close()
    return data

def cottage_attributes_relation_exists(cot_id):
    """Check if a cottage attribute relation exists for a given cottage ID."""
    connection = create_connection()
    if connection is None:
        return False

    try:
        cursor = connection.cursor()
        query = "SELECT COUNT(1) FROM COTTAGE_ATTRIBUTES_RELATION WHERE cot_id = %s"
        cursor.execute(query, (cot_id,))
        result = cursor.fetchone()
        return result and result[0] > 0
    except Error as e:
        st.error(f"Error while checking attribute relation: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def update_cottage_attributes_with_new_fields(
    cot_id, pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
    cot_toilet_id, has_balcony, cot_storey_id, aircond_id, kitchen_type_id, parking_type_id
):
    """Update attributes for a cottage with new fields."""
    connection = create_connection()
    if connection is None:
        st.error("Database connection failed.")
        return

    try:
        cursor = connection.cursor()

        # Insert if relation doesn't exist
        if not cottage_attributes_relation_exists(cot_id):
            query = """
            INSERT INTO COTTAGE_ATTRIBUTES_RELATION
            (cot_id, pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
            cot_toilet_id, cot_storey_id, aircond_id, kitchen_type_id, parking_type_id, cot_balcony_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (cot_id, pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
                                   cot_toilet_id, cot_storey_id, aircond_id, kitchen_type_id, parking_type_id, has_balcony))
        else:
            # Update existing relation
            query = """
            UPDATE COTTAGE_ATTRIBUTES_RELATION
            SET pool_id = %s, loc_id = %s, room_id = %s, max_pax_id = %s, ct_id = %s, ct_id_stat = %s,
                cot_toilet_id = %s, cot_storey_id = %s, aircond_id = %s, kitchen_type_id = %s,
                parking_type_id = %s, cot_balcony_id = %s
            WHERE cot_id = %s
            """
            cursor.execute(query, (pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
                                   cot_toilet_id, cot_storey_id, aircond_id, kitchen_type_id, parking_type_id, has_balcony, cot_id))

        connection.commit()
        rows_affected = cursor.rowcount
        if rows_affected > 0:
            st.success(f"Cottage attributes updated successfully for Cottage ID: {cot_id}")
            st.rerun()
        else:
            st.warning(f"No rows were updated for Cottage ID: {cot_id}.")
    except Error as e:
        st.error(f"Error occurred: {e}")
    finally:
        cursor.close()
        connection.close()

def manage_cottage_table():
    """Streamlit interface for managing the COTTAGE table."""
    st.subheader("Manage Cottages")

    connection = create_connection()
    if connection is None:
        return

    try:
        # Fetch current data from the COTTAGE table
        query = "SELECT * FROM COTTAGE"
        cottage_df = pd.read_sql(query, connection)
    except Error as e:
        st.error(f"Error while fetching cottages: {e}")
        return
    finally:
        connection.close()

    # Display current cottages
    st.subheader("Existing Cottages")
    st.dataframe(cottage_df)

    # Add New Cottage
    st.subheader("Add New Cottage")
    with st.form("add_cottage_form"):
        new_cot_name = st.text_input("Cottage Name")
        new_cot_price = st.number_input("Cottage Price", min_value=0.0, format="%.2f")
        add_submit = st.form_submit_button("Add Cottage")

        if add_submit:
            if new_cot_name and new_cot_price > 0:
                connection = create_connection()
                if connection:
                    try:
                        cursor = connection.cursor()
                        query = "INSERT INTO COTTAGE (cot_name, cot_price) VALUES (%s, %s)"
                        cursor.execute(query, (new_cot_name, new_cot_price))
                        connection.commit()
                        st.success("Cottage added successfully!")
                        st.experimental_rerun()
                    except Error as e:
                        st.error(f"Error while adding cottage: {e}")
                    finally:
                        cursor.close()
                        connection.close()
            else:
                st.error("Cottage name and price must be provided.")

    # Edit Existing Cottage
    st.subheader("Edit Cottage")
    selected_cot_id = st.selectbox(
        "Select Cottage ID to Edit",
        options=cottage_df['cot_id'].tolist()
    )

    selected_cottage = cottage_df[cottage_df['cot_id'] == selected_cot_id].iloc[0]
    with st.form("edit_cottage_form"):
        edit_cot_name = st.text_input("Cottage Name", value=selected_cottage['cot_name'])
        edit_cot_price = st.number_input(
            "Cottage Price", value=selected_cottage['cot_price'], min_value=0.0, format="%.2f"
        )
        edit_submit = st.form_submit_button("Update Cottage")

        if edit_submit:
            if edit_cot_name and edit_cot_price > 0:
                connection = create_connection()
                if connection:
                    try:
                        cursor = connection.cursor()
                        query = "UPDATE COTTAGE SET cot_name = %s, cot_price = %s WHERE cot_id = %s"
                        cursor.execute(query, (edit_cot_name, edit_cot_price, selected_cot_id))
                        connection.commit()
                        st.success(f"Cottage ID {selected_cot_id} updated successfully!")
                        st.experimental_rerun()
                    except Error as e:
                        st.error(f"Error while updating cottage: {e}")
                    finally:
                        cursor.close()
                        connection.close()
            else:
                st.error("Cottage name and price must be valid.")

    # Delete Cottage
    st.subheader("Delete Cottage")
    del_cot_id = st.selectbox(
        "Select Cottage ID to Delete",
        options=cottage_df['cot_id'].tolist()
    )

    if st.button("Delete Cottage"):
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = "DELETE FROM COTTAGE WHERE cot_id = %s"
                cursor.execute(query, (del_cot_id,))
                connection.commit()
                st.success(f"Cottage ID {del_cot_id} deleted successfully!")
                st.experimental_rerun()
            except Error as e:
                st.error(f"Error while deleting cottage: {e}")
            finally:
                cursor.close()
                connection.close()



def show_cottage_management():
    """Streamlit interface for cottage management."""
    st.title("Cottage Management")

    # Fetch data
    all_data = fetch_all_data()
    if all_data is None:
        return

    # Extracting tables
    cottage_df = all_data['COTTAGE']
    pool_df = all_data['POOL']
    loc_df = all_data['LOCATION']
    room_df = all_data['ROOM']
    max_pax_df = all_data['MAXIMUM_PAX']
    ct_df = all_data['COTTAGE_TYPES']
    ct_stat_df = all_data['COTTAGE_STATUS']
    toilet_df = all_data['COTTAGE_TOILET']
    balcony_df = all_data['COTTAGE_BALCONY']
    storey_df = all_data['COTTAGE_STOREY']
    aircond_df = all_data['AIRCOND_ROOM']
    kitchen_df = all_data['KITCHEN_TYPES']
    parking_df = all_data['PARKING_TYPES']
    cottage_attr_rel_df = all_data['COTTAGE_ATTRIBUTES_RELATION']

    # Display Cottage Table
    st.subheader("Cottages Table")
    st.dataframe(cottage_df)

    # Display COTTAGE_ATTRIBUTES_RELATION Table
    st.subheader("Current Cottage Attributes Relationships")
    st.dataframe(cottage_attr_rel_df)

    # Assign Attributes to Cottage
    st.subheader("Assign Attributes to Cottage")
    selected_cot_id = st.selectbox(
        "Select Cottage ID",
        cottage_df['cot_id'].tolist()
    )

    # Check for empty DataFrames and handle None values
    if pool_df.empty:
        st.warning("No Pool data available.")
        return
    pool_id = st.selectbox(
        "Select Pool",
        options=pool_df.apply(
            lambda x: f"{x['pool_id']} - {x['pool_detail'] if x['pool_detail'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not pool_df.empty else None

    if loc_df.empty:
        st.warning("No Location data available.")
        return
    loc_id = st.selectbox(
        "Select Location",
        options=loc_df.apply(
            lambda x: f"{x['loc_id']} - {x['loc_details'] if x['loc_details'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not loc_df.empty else None

    if room_df.empty:
        st.warning("No Room data available.")
        return
    room_id = st.selectbox(
        "Select Room",
        options=room_df.apply(
            lambda x: f"{x['room_id']} - {x['room_details'] if x['room_details'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not room_df.empty else None

    if max_pax_df.empty:
        st.warning("No Max Pax data available.")
        return
    max_pax_id = st.selectbox(
        "Select Max Pax",
        options=max_pax_df.apply(
            lambda x: f"{x['max_pax_id']} - {x['max_pax_details'] if x['max_pax_details'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not max_pax_df.empty else None

    if ct_df.empty:
        st.warning("No Cottage Type data available.")
        return
    ct_id = st.selectbox(
        "Select Cottage Type",
        options=ct_df.apply(
            lambda x: f"{x['ct_id']} - {x['ct_details'] if x['ct_details'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not ct_df.empty else None

    if ct_stat_df.empty:
        st.warning("No Cottage Status data available.")
        return
    ct_id_stat = st.selectbox(
        "Select Cottage Status",
        options=ct_stat_df.apply(
            lambda x: f"{x['cottage_status_id']} - {x['ct_status_details'] if x['ct_status_details'] else 'No Details'}", axis=1
        ).tolist()
    ).split(' ')[0] if not ct_stat_df.empty else None

    has_balcony = st.radio(
        "Does the Cottage have a Balcony?",
        options=[True, False],
        format_func=lambda x: "Yes" if x else "No"
    )

    if toilet_df.empty:
        st.warning("No Toilet data available.")
        return
    cot_toilet_id = st.selectbox(
        "Select Toilet",
        options=toilet_df['cot_toilet_id'].tolist()
    ) if not toilet_df.empty else None

    if storey_df.empty:
        st.warning("No Storey data available.")
        return
    cot_storey_id = st.selectbox(
        "Select Storey",
        options=storey_df['cot_storey_id'].tolist()
    ) if not storey_df.empty else None

    if aircond_df.empty:
        st.warning("No Aircondition data available.")
        return
    aircond_id = st.selectbox(
        "Select Aircondition",
        options=aircond_df['aircond_id'].tolist()
    ) if not aircond_df.empty else None

    if kitchen_df.empty:
        st.warning("No Kitchen data available.")
        return
    kitchen_type_id = st.selectbox(
        "Select Kitchen Type",
        options=kitchen_df['kitchen_type_id'].tolist()
    ) if not kitchen_df.empty else None

    if parking_df.empty:
        st.warning("No Parking data available.")
        return
    parking_type_id = st.selectbox(
        "Select Parking Type",
        options=parking_df['parking_type_id'].tolist()
    ) if not parking_df.empty else None

    # Update the attributes for the selected cottage
    if st.button("Update Cottage Attributes"):
        update_cottage_attributes_with_new_fields(
            selected_cot_id, pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
            cot_toilet_id, has_balcony, cot_storey_id, aircond_id, kitchen_type_id, parking_type_id
        )

if __name__ == "__main__":
    # Sidebar navigation or tabs for better user experience
    st.sidebar.title("Navigation")
    options = ["Manage Cottage Attributes", "Manage Cottage Table"]
    choice = st.sidebar.radio("Choose an option", options)

    if choice == "Manage Cottage Attributes":
        show_cottage_management()
    elif choice == "Manage Cottage Table":
        manage_cottage_table()
