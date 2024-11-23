import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd

# Database configuration (update as necessary)
DB_CONFIG = {
    host=db_config["host"],
    port=db_config["port"],
    user=db_config["user"],
    password=db_config["password"],
    database=db_config["database"]
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

    pool_id = st.selectbox(
        "Select Pool",
        options=pool_df.apply(lambda x: f"{x['pool_id']} - {x['pool_detail']}", axis=1).tolist()
    ).split(' ')[0]

    loc_id = st.selectbox(
        "Select Location",
        options=loc_df.apply(lambda x: f"{x['loc_id']} - {x['loc_details']}", axis=1).tolist()
    ).split(' ')[0]

    room_id = st.selectbox(
        "Select Room",
        options=room_df.apply(lambda x: f"{x['room_id']} - {x['room_details']}", axis=1).tolist()
    ).split(' ')[0]

    max_pax_id = st.selectbox(
        "Select Max Pax",
        options=max_pax_df.apply(lambda x: f"{x['max_pax_id']} - {x['max_pax_details']}", axis=1).tolist()
    ).split(' ')[0]

    ct_id = st.selectbox(
        "Select Cottage Type",
        options=ct_df.apply(lambda x: f"{x['ct_id']} - {x['ct_details']}", axis=1).tolist()
    ).split(' ')[0]

    ct_id_stat = st.selectbox(
        "Select Cottage Status",
        options=ct_stat_df.apply(lambda x: f"{x['cottage_status_id']} - {x['ct_status_details']}", axis=1).tolist()
    ).split(' ')[0]

    has_balcony = st.radio(
        "Does the Cottage have a Balcony?",
        options=[True, False],
        format_func=lambda x: "Yes" if x else "No"
    )

    toilet_id = st.selectbox(
        "Select Number of Toilets",
        toilet_df.apply(lambda x: f"{x['cot_toilet_id']} - {x['num_toilets']}", axis=1).tolist()
    ).split(' ')[0]

    storey_id = st.selectbox(
        "Select Number of Storeys",
        storey_df.apply(lambda x: f"{x['cot_storey_id']} - {x['num_storeys']}", axis=1).tolist()
    ).split(' ')[0]

    aircond_id = st.selectbox(
        "Select Air Conditioning Unit",
        aircond_df.apply(lambda x: f"{x['aircond_id']} - {x['aircond_unit']}", axis=1).tolist()
    ).split(' ')[0]

    kitchen_type_id = st.selectbox(
        "Select Kitchen Type",
        kitchen_df.apply(lambda x: f"{x['kitchen_type_id']} - {x['kitchen_type_name']}", axis=1).tolist()
    ).split(' ')[0]

    parking_type_id = st.selectbox(
        "Select Parking Type",
        parking_df.apply(lambda x: f"{x['parking_type_id']} - {x['parking_type_name']}", axis=1).tolist()
    ).split(' ')[0]

    if st.button("Update Attributes"):
        update_cottage_attributes_with_new_fields(
            selected_cot_id, pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat,
            toilet_id, has_balcony, storey_id, aircond_id, kitchen_type_id, parking_type_id
        )

# Run the Streamlit app
if __name__ == "__main__":
    show_cottage_management()
