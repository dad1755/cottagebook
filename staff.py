import streamlit as st
from sqlalchemy import create_engine, text

# Database connection setup
DATABASE_URL = "mysql+mysqlconnector://root:altisBGP@192@0.tcp.ap.ngrok.io:11157/sql12741294"
engine = create_engine(DATABASE_URL)

# Load data function
def load_data(query, parameters=None):
    """Load data from the database using the given query."""
    with engine.connect() as connection:
        result = connection.execute(text(query), parameters or {})
        return [dict(row) for row in result]

# Save data function
def save_data(query, parameters=None):
    """Save data to the database using the given query."""
    with engine.connect() as connection:
        connection.execute(text(query), parameters or {})

def staff_role_section():
    """Display the section for managing staff and roles."""
    st.header("Manage Staff and Roles")

    manage_roles()
    manage_staff()

# Role Management
def manage_roles():
    """Display, add, update, and delete roles."""
    st.subheader("Manage Roles")

    # Function to fetch roles from the database
    def fetch_roles():
        roles = load_data("SELECT * FROM Role")
        print("Fetched Roles from DB:", roles)  # Debugging line
        return roles

    # Load roles initially or from session state
    if 'roles' not in st.session_state:
        st.session_state.roles = fetch_roles()  # Initial fetch of roles

    # Add Role
    new_role_name = st.text_input("New Role Name")
    if st.button("Add Role"):
        if new_role_name:
            try:
                # Insert the new role into the database without specifying role_id
                save_data("INSERT INTO Role (role_name) VALUES (:role_name)", {"role_name": new_role_name})
                st.success("Role added successfully.")
                # Refresh the list of roles after adding a new one
                st.session_state.roles = fetch_roles()  # Re-fetch roles from DB
                print("Roles after adding:", st.session_state.roles)  # Debugging line
            except Exception as e:
                st.error(f"Error adding role: {e}")  # Show error in Streamlit UI
                print("Error adding role:", e)  # Debugging line
        else:
            st.warning("Please enter a role name.")

    # Display roles
    if st.session_state.roles:
        st.write("Available Roles:")
        for role in st.session_state.roles:
            role_id = role['role_id']
            current_name = role['role_name']
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                new_name = st.text_input(f"Edit Role {role_id} Name", current_name, key=f"role_{role_id}")
            with col2:
                if st.button("Update", key=f"update_role_{role_id}"):
                    if new_name and new_name != current_name:
                        save_data("UPDATE Role SET role_name = :new_name WHERE role_id = :role_id", 
                                  {"new_name": new_name, "role_id": role_id})
                        st.success("Role updated.")
                        st.session_state.roles = fetch_roles()  # Refresh roles after updating
            with col3:
                if st.button("Delete", key=f"delete_role_{role_id}"):
                    save_data("DELETE FROM Role WHERE role_id = :role_id", {"role_id": role_id})
                    st.success("Role deleted.")
                    st.session_state.roles = fetch_roles()  # Refresh roles after deleting
    else:
        st.write("No roles found.")




# Staff Management
def manage_staff():
    """Display, add, update, and delete staff members."""
    st.subheader("Manage Staff")
    staff_members = load_data("SELECT * FROM Staff")
    roles = load_data("SELECT * FROM Role")
    role_options = {role['role_id']: role['role_name'] for role in roles}

    # Adding new staff member
    new_staff_name = st.text_input("New Staff Name")
    new_staff_email = st.text_input("New Staff Email")
    new_staff_phone = st.text_input("New Staff Phone")
    new_staff_role_id = st.selectbox("Role", list(role_options.keys()), format_func=lambda x: role_options[x])
    
    if st.button("Add Staff"):
        if new_staff_name and new_staff_email and new_staff_phone:
            save_data("""
                INSERT INTO Staff (staff_name, staff_phone, staff_email, role_id)
                VALUES (:name, :phone, :email, :role_id)
            """, {"name": new_staff_name, "phone": new_staff_phone, "email": new_staff_email, "role_id": new_staff_role_id})
            st.success("Staff added successfully.")

    # Display staff members
    if staff_members:
        st.write("Available Staff:")
        for staff in staff_members:
            st.write(f"Staff ID: {staff['staff_id']}, Name: {staff['staff_name']}, Email: {staff['staff_email']}")
            
            new_name = st.text_input(f"Edit Name for Staff {staff['staff_id']}", staff['staff_name'], key=f"staff_name_{staff['staff_id']}")
            new_phone = st.text_input(f"Edit Phone for Staff {staff['staff_id']}", staff['staff_phone'], key=f"staff_phone_{staff['staff_id']}")
            new_role_id = st.selectbox(f"Edit Role for Staff {staff['staff_id']}", list(role_options.keys()), 
                                       index=list(role_options.keys()).index(staff['role_id']), format_func=lambda x: role_options[x])
            
            if st.button("Update", key=f"update_staff_{staff['staff_id']}"):
                save_data("""
                    UPDATE Staff SET staff_name = :name, staff_phone = :phone, role_id = :role_id WHERE staff_id = :staff_id
                """, {"name": new_name, "phone": new_phone, "role_id": new_role_id, "staff_id": staff['staff_id']})
                st.success("Staff updated.")
            
            if st.button("Delete", key=f"delete_staff_{staff['staff_id']}"):
                save_data("DELETE FROM Staff WHERE staff_id = :staff_id", {"staff_id": staff['staff_id']})
                st.success("Staff deleted.")
    else:
        st.write("No staff members found.")

# Run the application
if __name__ == "__main__":
    staff_role_section()
