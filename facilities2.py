import streamlit as st
import mysql.connector
from mysql.connector import Error

# Database configuration (update as necessary)
DB_CONFIG = {
    'host': '0.tcp.ap.ngrok.io',  # ngrok host
    'database': 'sql12741294',     # Your database name
    'user': 'root',                # MySQL user
    'password': 'altisBGP@192',    # MySQL password
    'port': 11157             # ngrok port
}

def execute_query(query, params=None):
    """Execute a query with optional parameters."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        st.success("Query executed successfully.")
        return cursor
    except Error as e:
        st.error(f"Error executing query: {query} with params: {params} | Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def fetch_data(query):
    """Fetch data from the database."""
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        st.error(f"Error: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# CRUD Functions for Cottage Toilet
def create_cottage_toilet(num_toilets):
    query = "INSERT INTO COTTAGE_TOILET (num_toilets) VALUES (%s)"
    execute_query(query, (num_toilets,))

def get_cottage_toilets():
    query = "SELECT * FROM COTTAGE_TOILET"
    return fetch_data(query) or []

def update_cottage_toilet(cot_toilet_id, num_toilets):
    query = "UPDATE COTTAGE_TOILET SET num_toilets = %s WHERE cot_toilet_id = %s"
    execute_query(query, (num_toilets, cot_toilet_id))

def delete_cottage_toilet(cot_toilet_id):
    query = "DELETE FROM COTTAGE_TOILET WHERE cot_toilet_id = %s"
    execute_query(query, (cot_toilet_id,))

# CRUD Functions for Cottage Balcony
def create_cottage_balcony(has_balcony):
    has_balcony_value = "Yes" if has_balcony == "Yes" else "No"
    query = "INSERT INTO COTTAGE_BALCONY (has_balcony) VALUES (%s)"
    execute_query(query, (has_balcony_value,))

def get_cottage_balconies():
    query = "SELECT * FROM COTTAGE_BALCONY"
    return fetch_data(query) or []

def update_cottage_balcony(cot_balcony_id, has_balcony):
    has_balcony_value = "Yes" if has_balcony == "Yes" else "No"
    query = "UPDATE COTTAGE_BALCONY SET has_balcony = %s WHERE cot_balcony_id = %s"
    execute_query(query, (has_balcony_value, cot_balcony_id))

def delete_cottage_balcony(cot_balcony_id):
    query = "DELETE FROM COTTAGE_BALCONY WHERE cot_balcony_id = %s"
    execute_query(query, (cot_balcony_id,))

# CRUD Functions for Cottage Storey
def create_cottage_storey(num_storeys):
    query = "INSERT INTO COTTAGE_STOREY (num_storeys) VALUES (%s)"
    execute_query(query, (num_storeys,))

def get_cottage_storeys():
    query = "SELECT * FROM COTTAGE_STOREY"
    return fetch_data(query) or []

def update_cottage_storey(cot_storey_id, num_storeys):
    query = "UPDATE COTTAGE_STOREY SET num_storeys = %s WHERE cot_storey_id = %s"
    execute_query(query, (num_storeys, cot_storey_id))

def delete_cottage_storey(cot_storey_id):
    query = "DELETE FROM COTTAGE_STOREY WHERE cot_storey_id = %s"
    execute_query(query, (cot_storey_id,))

# CRUD Functions for Air Conditioning Room
def create_aircond_room(aircond_unit):
    query = "INSERT INTO AIRCOND_ROOM (aircond_unit) VALUES (%s)"
    execute_query(query, (aircond_unit,))

def get_aircond_rooms():
    query = "SELECT * FROM AIRCOND_ROOM"
    return fetch_data(query) or []

def update_aircond_room(aircond_id, aircond_unit):
    query = "UPDATE AIRCOND_ROOM SET aircond_unit = %s WHERE aircond_id = %s"
    execute_query(query, (aircond_unit, aircond_id))

def delete_aircond_room(aircond_id):
    query = "DELETE FROM AIRCOND_ROOM WHERE aircond_id = %s"
    execute_query(query, (aircond_id,))

# CRUD Functions for Kitchen Types
def create_kitchen_type(kitchen_type_name):
    query = "INSERT INTO KITCHEN_TYPES (kitchen_type_name) VALUES (%s)"
    execute_query(query, (kitchen_type_name,))

def get_kitchen_types():
    query = "SELECT * FROM KITCHEN_TYPES"
    return fetch_data(query) or []

def update_kitchen_type(kitchen_type_id, kitchen_type_name):
    query = "UPDATE KITCHEN_TYPES SET kitchen_type_name = %s WHERE kitchen_type_id = %s"
    execute_query(query, (kitchen_type_name, kitchen_type_id))

def delete_kitchen_type(kitchen_type_id):
    query = "DELETE FROM KITCHEN_TYPES WHERE kitchen_type_id = %s"
    execute_query(query, (kitchen_type_id,))

# CRUD Functions for Parking Types
def create_parking_type(parking_type_name):
    query = "INSERT INTO PARKING_TYPES (parking_type_name) VALUES (%s)"
    execute_query(query, (parking_type_name,))

def get_parking_types():
    query = "SELECT * FROM PARKING_TYPES"
    return fetch_data(query) or []

def update_parking_type(parking_type_id, parking_type_name):
    query = "UPDATE PARKING_TYPES SET parking_type_name = %s WHERE parking_type_id = %s"
    execute_query(query, (parking_type_name, parking_type_id))

def delete_parking_type(parking_type_id):
    query = "DELETE FROM PARKING_TYPES WHERE parking_type_id = %s"
    execute_query(query, (parking_type_id,))

# Streamlit UI
def show_facilities2_management():
    st.write("### Facilities Management - V2 🏢")

    # Cottage Toilet Management
    st.write("#### Cottage Toilet Management")
    num_toilets = st.number_input("Number of Toilets", min_value=1)
    if st.button("Add Cottage Toilet"):
        create_cottage_toilet(num_toilets)

    toilets_data = get_cottage_toilets()
    if toilets_data:
        st.dataframe(toilets_data)

        # Update and Delete functionality for Cottage Toilets
        cot_toilet_id = st.selectbox("Select Cottage Toilet to Update/Delete", [t['cot_toilet_id'] for t in toilets_data])
        if st.button("Update Cottage Toilet"):
            update_num_toilets = st.number_input("Update Number of Toilets", min_value=1)
            update_cottage_toilet(cot_toilet_id, update_num_toilets)

        if st.button("Delete Cottage Toilet"):
            delete_cottage_toilet(cot_toilet_id)

    # Cottage Balcony Management
    st.write("#### Cottage Balcony Management")
    has_balcony = st.selectbox("Does the Cottage have a Balcony?", options=["Yes", "No"])
    if st.button("Add Cottage Balcony"):
        create_cottage_balcony(has_balcony)

    balconies_data = get_cottage_balconies()
    if balconies_data:
        st.dataframe(balconies_data)

        # Update and Delete functionality for Cottage Balconies
        cot_balcony_id = st.selectbox("Select Cottage Balcony to Update/Delete", [b['cot_balcony_id'] for b in balconies_data])
        if st.button("Update Cottage Balcony"):
            update_has_balcony = st.selectbox("Update Balcony Status", options=["Yes", "No"])
            update_cottage_balcony(cot_balcony_id, update_has_balcony)

        if st.button("Delete Cottage Balcony"):
            delete_cottage_balcony(cot_balcony_id)

    # Cottage Storey Management
    st.write("#### Cottage Storey Management")
    num_storeys = st.number_input("Number of Storeys", min_value=1)
    if st.button("Add Cottage Storey"):
        create_cottage_storey(num_storeys)

    storeys_data = get_cottage_storeys()
    if storeys_data:
        st.dataframe(storeys_data)

        # Update and Delete functionality for Cottage Storeys
        cot_storey_id = st.selectbox("Select Cottage Storey to Update/Delete", [s['cot_storey_id'] for s in storeys_data])
        if st.button("Update Cottage Storey"):
            update_num_storeys = st.number_input("Update Number of Storeys", min_value=1)
            update_cottage_storey(cot_storey_id, update_num_storeys)

        if st.button("Delete Cottage Storey"):
            delete_cottage_storey(cot_storey_id)

    # Air Conditioning Room Management
    st.write("#### Air Conditioning Room Management")
    aircond_unit = st.text_input("Air Conditioning Unit Name")
    if st.button("Add Air Conditioning Room"):
        create_aircond_room(aircond_unit)

    aircond_rooms_data = get_aircond_rooms()
    if aircond_rooms_data:
        st.dataframe(aircond_rooms_data)

        # Update and Delete functionality for Air Conditioning Rooms
        aircond_id = st.selectbox("Select Air Conditioning Room to Update/Delete", [a['aircond_id'] for a in aircond_rooms_data])
        if st.button("Update Air Conditioning Room"):
            update_aircond_unit = st.text_input("Update Air Conditioning Unit Name")
            update_aircond_room(aircond_id, update_aircond_unit)

        if st.button("Delete Air Conditioning Room"):
            delete_aircond_room(aircond_id)

    # Kitchen Type Management
    st.write("#### Kitchen Type Management")
    kitchen_type_name = st.text_input("Kitchen Type Name")
    if st.button("Add Kitchen Type"):
        create_kitchen_type(kitchen_type_name)

    kitchen_types_data = get_kitchen_types()
    if kitchen_types_data:
        st.dataframe(kitchen_types_data)

        # Update and Delete functionality for Kitchen Types
        kitchen_type_id = st.selectbox("Select Kitchen Type to Update/Delete", [k['kitchen_type_id'] for k in kitchen_types_data])
        if st.button("Update Kitchen Type"):
            update_kitchen_type_name = st.text_input("Update Kitchen Type Name")
            update_kitchen_type(kitchen_type_id, update_kitchen_type_name)

        if st.button("Delete Kitchen Type"):
            delete_kitchen_type(kitchen_type_id)

    # Parking Type Management
    st.write("#### Parking Type Management")
    parking_type_name = st.text_input("Parking Type Name")
    if st.button("Add Parking Type"):
        create_parking_type(parking_type_name)

    parking_types_data = get_parking_types()
    if parking_types_data:
        st.dataframe(parking_types_data)

        # Update and Delete functionality for Parking Types
        parking_type_id = st.selectbox("Select Parking Type to Update/Delete", [p['parking_type_id'] for p in parking_types_data])
        if st.button("Update Parking Type"):
            update_parking_type_name = st.text_input("Update Parking Type Name")
            update_parking_type(parking_type_id, update_parking_type_name)

        if st.button("Delete Parking Type"):
            delete_parking_type(parking_type_id)

# Main application logic
if __name__ == "__main__":
    show_facilities2_management()
