import streamlit as st
from db import load_data, save_data

def approve_payment_section():
    st.header("Approve Payment")

    pending_bookings = load_data("SELECT * FROM Reservation WHERE payment_status = 'pending'")
    
    if pending_bookings:
        for booking in pending_bookings:
            st.write(f"Booking ID: {booking['reserve_id']}, Cottage ID: {booking['cottage_id']}, Total Price: {booking['total_price']}")
    else:
        st.write("No pending bookings.")
    
    payment_id = st.text_input("Enter Payment ID to Approve", key="payment_id_input")
    if st.button("Approve Payment", key="approve_payment_button"):
        if payment_id:
            update_payment_query = "UPDATE Payment SET status = 'approved' WHERE payment_id = :payment_id"
            save_data(update_payment_query, {"payment_id": payment_id})
            st.success("Payment approved.")
        else:
            st.warning("Please enter a valid Payment ID.")
