from tkinter import *
from tkinter.messagebox import *
import re
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['feedback_db']
collection = db['feedback_collection']


def add_feedback():
    name = entry_name.get()
    if (name == "") or (name.strip() == ""):
        showerror("ERROR", "Name Can't be Empty")
    elif (not name.isalpha()):
        showerror("ERROR", "Invalid Name")
        entry_name.delete(0, END)
        entry_name.focus()
        return

    email = entry_email.get()
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if (email == "") or (email.strip() == "") or not (re.fullmatch(regex, email)):
        showerror("ERROR", "Invalid Email")
        entry_email.delete(0, END)
        entry_email.focus()
        return

    message = text_feedback.get('1.0', END)
    if (message == "") or (message.strip() == ""):
        showerror("ERROR", "Please Fill Feedback")
        text_feedback.focus()
        return

    rating = rating_var.get()

    if name and email and message:
        feedback = {
            'name': name,
            'email': email,
            'message': message,
            'rating': rating
        }
        collection.insert_one(feedback)
        showinfo("Success", "Feedback added successfully.")
        clear_fields()
    else:
        showwarning("Error", "Please fill in all fields.")


def admin_login():
    username = entry_username.get()
    password = entry_password.get()

    # Perform authentication
    if username == 'admin' and password == 'password':
        admin_window = Toplevel(window)
        admin_window.title("Admin Panel")
        admin_window.geometry("500x500")
        admin_window.configure(bg='#8F00FF')
        admin_window.iconbitmap("f.ico")

        # Create feedback list box in the admin window
        feedback_list_admin = Listbox(admin_window, height=20, width=80)
        feedback_list_admin.grid(row=0, columnspan=3, padx=10, pady=10)

        # Retrieve and display all feedbacks in the admin window
        display_feedback_admin(feedback_list_admin)

        # Create delete button
        button_delete = Button(admin_window, text="Delete Feedback", command=lambda: delete_feedback_admin(feedback_list_admin))
        button_delete.grid(row=1, column=0, padx=10, pady=10)

        # Create logout button
        button_logout = Button(admin_window, text="Logout", command=admin_window.destroy)
        button_logout.grid(row=1, column=1, padx=10, pady=10)

    else:
        showerror("Error", "Invalid credentials")


def display_feedback_admin(listbox):
    feedbacks = collection.find()
    listbox.delete(0, END)
    for feedback in feedbacks:
        name = feedback.get('name', '')
        email = feedback.get('email', '')
        message = feedback.get('message', '')
        rating = feedback.get('rating', '')
        listbox.insert(END, f"Name: {name}\nEmail: {email}\nMessage: {message}\nRating: {rating}/5\n")


def delete_feedback_admin(listbox):
    selected_index = listbox.curselection()
    if selected_index:
        confirmation = askyesno("Confirmation", "Are you sure you want to delete this feedback?")
        if confirmation:
            feedback = listbox.get(selected_index)
            name, email, _ = feedback.split('\n')[:3]
            name = name.split(': ')[1]
            email = email.split(': ')[1]
            collection.delete_one({'name': name, 'email': email})
            showinfo("Success", "Feedback deleted successfully.")
            display_feedback_admin(listbox)
    else:
        showwarning("Error", "Please select a feedback to delete.")


def clear_fields():
    entry_name.delete(0, END)
    entry_email.delete(0, END)
    text_feedback.delete('1.0', END)
    rating_var.set(5)


# Create the main window
window = Tk()
window.title("Feedback Management App")
window.configure(bg='#8F00FF')
f = ("Arial", 10, "bold")
window.iconbitmap("f.ico")

# Create labels
label_name = Label(window, text="Name:", font=f)
label_name.grid(row=0, column=0, padx=10, pady=10)
label_email = Label(window, text="Email:", font=f)
label_email.grid(row=1, column=0, padx=10, pady=10)
label_feedback = Label(window, text="Feedback:", font=f)
label_feedback.grid(row=2, column=0, padx=10, pady=10)
label_rating = Label(window, text="Rating:", font=f)
label_rating.grid(row=3, column=0, padx=10, pady=10)

# Create entry fields
entry_name = Entry(window, font=f)
entry_name.grid(row=0, column=1, padx=10, pady=10)
entry_email = Entry(window, font=f)
entry_email.grid(row=1, column=1, padx=10, pady=10)

# Create feedback text box
text_feedback = Text(window, height=5, width=30, font=f)
text_feedback.grid(row=2, column=1, padx=10, pady=10)

# Create rating scale
rating_var = IntVar()
rating_var.set(5)
rating_frame = Frame(window, bg='#8F00FF')
rating_frame.grid(row=3, column=1, padx=10, pady=10)
for i in range(1, 6):
    radio_button = Radiobutton(rating_frame, text=str(i), variable=rating_var, value=i, font=f, bg='#8F00FF')
    radio_button.pack(side=LEFT)

# Create buttons
button_add = Button(window, text="Add Feedback", command=add_feedback, font=f)
button_add.grid(row=4, column=0, padx=10, pady=10)
button_clear = Button(window, text="Clear Fields", command=clear_fields, font=f)
button_clear.grid(row=4, column=1, padx=10, pady=10)

# Admin Login
label_username = Label(window, text="Username:", font=f)
label_username.grid(row=5, column=0, padx=10, pady=10)
label_password = Label(window, text="Password:", font=f)
label_password.grid(row=6, column=0, padx=10, pady=10)

entry_username = Entry(window, font=f)
entry_username.grid(row=5, column=1, padx=10, pady=10)
entry_password = Entry(window, show="*", font=f)
entry_password.grid(row=6, column=1, padx=10, pady=10)

button_login = Button(window, text="Admin Login", command=admin_login, font=f)
button_login.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

window.mainloop()
