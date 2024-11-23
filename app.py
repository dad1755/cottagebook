#app.py file
import streamlit as st
from booking import show_booking
from housekeeping import show_housekeeping
from management import show_management

# Set the title of the app
st.title("Cottage Booking System Group 2")

# Create a sidebar with three options
st.sidebar.title("Menu")
option = st.sidebar.radio("Select an option:", ("Booking", "House Keeping", "Management"))

# Display content based on the selected option
if option == "Booking":
    show_booking()

elif option == "House Keeping":
    show_housekeeping()

elif option == "Management":
    show_management()
