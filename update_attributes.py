# update_attributes.py
import streamlit as st
from mysql.connector import Error
from your_cottage_module import DB_CONFIG, execute_query, fetch_data  # Adjust import based on your file structure

def update_cottage_attributes(cot_id):
    """Update attributes for a specific cottage."""
    # Fetch current attributes for the selected cottage
    query = "SELECT * FROM COTTAGE_ATTRIBUTES_RELATION WHERE cot_id = %s"
    current_attributes = fetch_data(query, (cot_id,))
    
    if not current_attributes:
        st.warning("No attributes found for the selected cottage.")
        return

    # Display current attributes for the user
    st.write("Current Attributes:")
    attributes_df = pd.DataFrame(current_attributes)
    st.dataframe(attributes_df)

    # Update fields
    pool_id = st.number_input("Pool ID", value=current_attributes[0]['pool_id'], min_value=0)
    loc_id = st.number_input("Location ID", value=current_attributes[0]['loc_id'], min_value=0)
    room_id = st.number_input("Room ID", value=current_attributes[0]['room_id'], min_value=0)
    max_pax_id = st.number_input("Max Pax ID", value=current_attributes[0]['max_pax_id'], min_value=0)
    ct_id = st.number_input("Cottage Type ID", value=current_attributes[0]['ct_id'], min_value=0)
    ct_id_stat = st.number_input("Cottage Status ID", value=current_attributes[0]['ct_id_stat'], min_value=0)

    if st.button("Update Attributes"):
        update_query = """
            UPDATE COTTAGE_ATTRIBUTES_RELATION
            SET pool_id = %s, loc_id = %s, room_id = %s, max_pax_id = %s, ct_id = %s, ct_id_stat = %s
            WHERE cot_id = %s
        """
        params = (pool_id, loc_id, room_id, max_pax_id, ct_id, ct_id_stat, cot_id)
        execute_query(update_query, params)
        st.success("Cottage attributes updated successfully.")
