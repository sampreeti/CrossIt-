import os
import streamlit as st


st.set_page_config(page_title="Task Manager", layout="wide", page_icon="📝")

# --------------------- FILE PATHS ----------------------- #
USER_FILE = "users.txt"

# ------------- User Authentication Functions ------------ #
def login_option():
    st.subheader("🔐 Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(user, pwd):
            print("success")
            st.session_state.logged_in = True
            st.session_state.username = user
            st.success("Logged in!")
            st.rerun()
            return True
        else:
            st.error("Invalid credentials")
            return False

def register_option():
    st.subheader("📝 Register")
    new_user = st.text_input("New Username")
    new_pwd = st.text_input("New Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pwd):
            st.success("Registration successful. You may now log in.")
        else:
            st.error("Username already exists.")


def logout():
    del st.session_state['user']
    st.experimental_set_query_params(code="/logout")


def load_users():
    users = {}
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            for line in f:
                username, password = line.strip().split(":")
                users[username] = password
    return users

def register_user(username,password):
    users = load_users()
    if username in users:
        print("Username already exists.")
        return None

    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{password}\n")
    print("Registration successful.")
    return username

def login_user(username,password):
    users = load_users()
    if username in users and users[username] == password:
        print("Login successful.")
        return True
    else:
        print("Invalid username or password.", users)
        return None


# ----------------- Task Generation Functions ------------------ #
# Generates a filename specific to the user.
def get_task_file(username):
    return f"tasks_{username}.txt"

def load_tasks(username):
    task_file = get_task_file(username)
    tasks = []
    if os.path.exists(task_file):
        with open(task_file, "r") as f:
            for line in f:
                status, task = line.strip().split("|", 1)
                tasks.append({"task": task, "completed": status == "1"})
    
    return tasks


def save_tasks(username, tasks):
    with open(get_task_file(username), "w") as f:
        for task in tasks:
            status = "1" if task["completed"] else "0"
            f.write(f"{status}|{task['task']}\n")



# -------------- CSS Style for form_submit_button ---------------#
# -------------------------------------------------------------- #
st.markdown("""
<style>
.stFormSubmitButton>button{
    height: auto;  /* Optional: allows the height to adjust based on padding */
    padding-top: 0.00000000001px !important;  /* Adjust the top padding */
    padding-bottom: -.000000000001px !important; /* Adjust the bottom padding */
    padding-left: .0005px !important;  /* Adjust the left padding */
    padding-right: .005px !important; /* Adjust the right padding */        
    background-color: #dff3ff !important;
    color: grey !important;
    border: none !important;
}
</style>""", unsafe_allow_html=True) 

# Edit task Funtion to handle edit actions
def edit_task(i, task_list):
    with st.form(key=f"edit_form_{i}", clear_on_submit=False, border=False):
        col_form1, col_form2 = st.columns([9,1])
        with col_form1:
            new_text = st.text_input(
                "Edit Task",
                value=st.session_state.get(f"edit_text_{i}", task_list[i]["task"]),
                key=f"edit_input_{i}",
                label_visibility="collapsed",
                placeholder="Edit your task..."
            )
        with col_form2: 
            save = st.form_submit_button("✅")
        
    if save:
        task_list[i]["task"] = new_text.strip()
        save_tasks(st.session_state.username, task_list)
        st.session_state[f"editing_task_{i}"] = False
        st.rerun()


# ---------------------- TASK MANAGEMENT ------------------------
def task_manager(username, password):
    st.title(":orange[CrossIt 📝]")
    st.write(":green[**_Cross It, Crush it!_**]")
    st.subheader(f"✅ Task Manager - {username}")
    
    # Load tasks
    if "task_list" not in st.session_state:
        st.session_state.task_list = load_tasks(username)

    task_list = st.session_state.task_list

    # ➕ Add task
    with st.form("Add Task", clear_on_submit=True, border=False):
        new_task = st.text_input("_New Task_")
        if st.form_submit_button("➕ Add Task"):
            task_list.append({"task": new_task, "completed": False})


    st.divider()

    # ✅ Handle edit/save/delete actions before rendering
    for i in range(len(task_list)):
        if st.session_state.get(f"save_edit_{i}"):
            updated_text = st.session_state.get(f"edit_text_{i}", "")
            task_list[i]["task"] = updated_text.strip()
            save_tasks(username, task_list)
            st.session_state[f"editing_task_{i}"] = False
            st.session_state[f"save_edit_{i}"] = False
            st.rerun()

        elif st.session_state.get(f"cancel_edit_{i}"):
            st.session_state[f"editing_task_{i}"] = False
            st.session_state[f"cancel_edit_{i}"] = False
            st.rerun()

        elif st.session_state.get(f"delete_task_{i}"):
            task_list.pop(i)
            save_tasks(username, task_list)
            st.session_state[f"delete_task_{i}"] = False
            st.rerun()


    # 🧾 Render Task List
    for i, task in enumerate(task_list):
        task_id = f"task_{i}"
        checkbox_key = f"completed_{i}"

        # ✅ Capture checkbox value BEFORE rendering layout
        checked = st.session_state.get(checkbox_key, task["completed"])

        # ✅ Sync state only if it changed
        if checked != task["completed"]:
            task["completed"] = checked
            save_tasks(st.session_state.username, task_list)
        
        col1, col2, col3, col4 = st.columns([0.05, 0.6, 0.15, 0.15])

        with col1:
            checkbox_key = f"completed_{i}"
            # Show the checkbox with the current status
            st.checkbox("", value=checked, key=checkbox_key)
     
        with col2:
            if st.session_state.get(f"editing_task_{i}"):
                edit_task(i, task_list)  # Render edit UI  
            else:
                st.markdown(f"{'~~' if task['completed'] else ''}{task['task']}{'~~' if task['completed'] else ''}")

        with col3:
            if st.session_state.get(f"editing_task_{i}"):
                if st.button("❌", key=f"cancel_edit_btn_{i}"):
                    st.session_state.clicked = True
                    st.session_state[f"cancel_edit_{i}"] = True
                    st.rerun()
            else:
                if st.button("✏️", key=f"edit_btn_{i}"):
                    st.session_state.clicked = True
                    st.session_state[f"editing_task_{i}"] = True
                    st.session_state[f"edit_text_{i}"] = task["task"]
                    st.rerun()  

        with col4:
            if st.button("🗑️", key=f"delete_btn_{i}"):
                st.session_state.clicked = True
                st.session_state[f"delete_task_{i}"] = True
                st.rerun()



# ------------------------ Streamlit App --------------------------- #
# ------------------------------------------------------------------ #
def main():

    # --------------- Session State -----------------
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "password" not in st.session_state:
        st.session_state.password = ""
    if "clicked" not in st.session_state:
        st.session_state.clicked = False

    
    st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        .stContainer {
            padding-top: 1rem;
            background-color: #000000;
            color: #ffffff;
            position: top;
        }
        </style>""",
        unsafe_allow_html=True,
    )

    st.markdown("""
        <style>
        [data-testid="stHeader"] {
            background: #dff3ff;
        }
        </style>""",
        unsafe_allow_html=True) 

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #dff3ff;
        }
        .stTitle {
        color: orange;
        font-size: 2rem;
        font-weight: bold;
        position: fixed;
        }
        </style>""",
        unsafe_allow_html=True,
    )
    


    # -------------- CSS Style for all st.button() ---------------#
    # ----------------------------------------------------------- #
    st.markdown("""
    <style>
    button[kind="secondary"] {
        height: auto;  /* Optional: allows the height to adjust based on padding */
        padding-top: -0.0001px !important;  /* Adjust the top padding */
        padding-bottom: -.0001px !important; /* Adjust the bottom padding */
        padding-left: .0005px !important;  /* Adjust the left padding */
        padding-right: .005px !important; /* Adjust the right padding */
        background-color: #dff3ff;
        border: none !important;
    }
    </style>""", unsafe_allow_html=True)
        
    # ----------------------- App Router ------------------------ #
    auth_col1, auth_col2, auth_col3 = st.columns([2.8,4.4,2.8])
    success = False
    with auth_col2:
        if not st.session_state.logged_in:
            st.title(":orange[CrossIt 📝]")
            st.write(":green[**_Cross It, Crush it!_**]")
            tab1, tab2 = st.tabs(["Login", "Register"])
            with tab1:
                success = login_option()
            with tab2:
                register_option()

    
    if st.session_state.logged_in:
        task_manager(st.session_state.username, st.session_state.password)
  


if __name__ == "__main__":
    main()
