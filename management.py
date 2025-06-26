import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import tabulate
from datetime import datetime


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'airport_management'
}


CURRENT_USER = None


def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error connecting to database: {err}")
        return None

def fetch_all(query, params=None):
    conn = get_db_connection()
    if not conn: return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        messagebox.showerror("Query Error", f"Error fetching data: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def fetch_one(query, params=None):
    conn = get_db_connection()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    except mysql.connector.Error as err:
        messagebox.showerror("Query Error", f"Error fetching data: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def execute_query(query, params=None):
    conn = get_db_connection()
    if not conn: return False, None
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
        return True, cursor.lastrowid # Return True and last inserted ID if applicable
    except mysql.connector.Error as err:
        conn.rollback()
        messagebox.showerror("Query Error", f"Error executing query: {err}")
        return False, None
    finally:
        cursor.close()
        conn.close()

# - Main Application Class -
class AirportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Airport Management System")
        self.geometry("800x600") # Adjust size as needed

        # Style for ttk widgets
        style = ttk.Style(self)
        style.theme_use("classic") # 'clam', 'alt', 'default', 'classic'

        # Container for frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_frame = None
        self.create_frames()
        self.show_frame("LoginPage")

    def create_frames(self):
        for F in (LoginPage, SignupPage, UserDashboardPage, AdminDashboardPage, BookFlightPage, ViewAvailableFlightsPage, ViewMyTicketsPage, EditTicketPage): # Add more frames here
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name, data=None):
        global CURRENT_USER
        if page_name == "LoginPage": # Reset user on logout/going to login
            CURRENT_USER = None

        frame = self.frames[page_name]
        if hasattr(frame, 'on_show'): # Call on_show if frame has it (to refresh data)
             frame.on_show(data)
        frame.tkraise()
        self.current_frame = frame

    def get_current_user_id(self):
        return CURRENT_USER['user_id'] if CURRENT_USER else None

    def get_food_options(self):
        foods = fetch_all("SELECT food_id, item_name, type FROM food_items ORDER BY type, item_name")
        return {f"{food['item_name']} ({food['type']})": food['food_id'] for food in foods}

#  GUI Pages

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0") # Light grey background

        tk.Label(self, text="Airport System Login", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)

        form_frame = tk.Frame(self, bg="#f0f0f0")
        form_frame.pack(pady=20, padx=30)

        tk.Label(form_frame, text="Phone Number:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.phone_entry = ttk.Entry(form_frame, font=("Arial", 12), width=30)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=10)

        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 12), width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)

        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Login", command=self.login, style="Accent.TButton").pack(side="left", padx=10, ipadx=10, ipady=5)
        ttk.Button(button_frame, text="Sign Up", command=lambda: controller.show_frame("SignupPage")).pack(side="left", padx=10, ipadx=10, ipady=5)

        # Style for accent button
        s = ttk.Style()
        s.configure("Accent.TButton", font=("Arial", 12, "bold"), foreground="white", background="#0078D7") # Blue color


    def login(self):
        global CURRENT_USER
        phone = self.phone_entry.get()
        password = self.password_entry.get()

        if not phone or not password:
            messagebox.showerror("Error", "Phone number and password are required.")
            return

        user = fetch_one("SELECT user_id, username, password, role FROM users WHERE phone_number = %s", (phone,))

        if user and user['password'] == password: # In real app: check hashed password
            CURRENT_USER = {'user_id': user['user_id'], 'username': user['username'], 'role': user['role']}
            messagebox.showinfo("Success", f"Welcome {user['username']}!")
            self.phone_entry.delete(0, tk.END) # Clear fields
            self.password_entry.delete(0, tk.END)
            if user['role'] == 'admin':
                self.controller.show_frame("AdminDashboardPage")
            else:
                self.controller.show_frame("UserDashboardPage")
        else:
            messagebox.showerror("Error", "Invalid phone number or password.")

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#f0f0f0")

        tk.Label(self, text="User Registration", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=20)

        form_frame = tk.Frame(self, bg="#f0f0f0")
        form_frame.pack(pady=20, padx=30)

        tk.Label(form_frame, text="Username:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.username_entry = ttk.Entry(form_frame, font=("Arial", 12), width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=10)

        tk.Label(form_frame, text="Password:", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 12), width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)

        tk.Label(form_frame, text="Confirm Password:", font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.confirm_password_entry = ttk.Entry(form_frame, show="*", font=("Arial", 12), width=30)
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=10)

        tk.Label(form_frame, text="Phone Number:", font=("Arial", 12), bg="#f0f0f0").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.phone_entry = ttk.Entry(form_frame, font=("Arial", 12), width=30)
        self.phone_entry.grid(row=3, column=1, padx=5, pady=10)

        button_frame = tk.Frame(self, bg="#f0f0f0")
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Register", command=self.register, style="Accent.TButton").pack(side="left", padx=10, ipadx=10, ipady=5)
        ttk.Button(button_frame, text="Back to Login", command=lambda: controller.show_frame("LoginPage")).pack(side="left", padx=10, ipadx=10, ipady=5)

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        phone = self.phone_entry.get()

        if not all([username, password, confirm_password, phone]):
            messagebox.showerror("Error", "All fields are required.")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        if not phone.isdigit() or len(phone) < 10: # Basic phone validation
            messagebox.showerror("Error", "Invalid phone number format (at least 10 digits).")
            return

        # Check if phone number already exists
        existing_user = fetch_one("SELECT user_id FROM users WHERE phone_number = %s", (phone,))
        if existing_user:
            messagebox.showerror("Error", "Phone number already registered.")
            return

        success, _ = execute_query("INSERT INTO users (username, password, phone_number) VALUES (%s, %s, %s)",
                                 (username, password, phone))
        if success:
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_password_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.controller.show_frame("LoginPage")
        else:
            messagebox.showerror("Error", "Registration failed. Please try again.")


class UserDashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#e0e0e0")

        self.welcome_label = tk.Label(self, text="", font=("Arial", 20, "bold"), bg="#e0e0e0")
        self.welcome_label.pack(pady=20)

        button_style = {"font": ("Arial", 12), "width": 25, "pady": 10}
        button_frame = tk.Frame(self, bg="#e0e0e0")
        button_frame.pack(expand=True)

        ttk.Button(button_frame, text="Book a Flight", command=lambda: controller.show_frame("BookFlightPage"), style="Dashboard.TButton").pack(pady=10)
        ttk.Button(button_frame, text="View Available Flights", command=lambda: controller.show_frame("ViewAvailableFlightsPage"), style="Dashboard.TButton").pack(pady=10)
        ttk.Button(button_frame, text="View My Tickets", command=lambda: controller.show_frame("ViewMyTicketsPage"), style="Dashboard.TButton").pack(pady=10)
        ttk.Button(button_frame, text="Edit/Cancel My Ticket", command=lambda: controller.show_frame("EditTicketPage"), style="Dashboard.TButton").pack(pady=10)
        ttk.Button(button_frame, text="Logout", command=lambda: controller.show_frame("LoginPage"), style="Dashboard.TButton").pack(pady=10)

        s = ttk.Style()
        s.configure("Dashboard.TButton", font=("Arial", 12), padding=10, width=25)


    def on_show(self, data=None): # Called when frame is shown
        if CURRENT_USER:
            self.welcome_label.config(text=f"Welcome, {CURRENT_USER['username']}!")
        else: # Should not happen if logic is correct
            self.welcome_label.config(text="User Dashboard")
            self.controller.show_frame("LoginPage") # Redirect if no user

class AdminDashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure(bg="#d0d0d0")

        self.welcome_label = tk.Label(self, text="", font=("Arial", 20, "bold"), bg="#d0d0d0")
        self.welcome_label.pack(pady=20)

        tk.Label(self, text="Admin functionalities (e.g., Manage Flights, Users) would go here.", font=("Arial", 14), bg="#d0d0d0").pack(pady=10)

        # Placeholder for admin actions, e.g., view all bookings
        ttk.Button(self, text="View All Bookings (Console)", command=self.view_all_bookings_console).pack(pady=10)
        ttk.Button(self, text="Manage Flights (Add/Edit - Future)", command=self.manage_flights_placeholder).pack(pady=10)
        ttk.Button(self, text="Logout", command=lambda: controller.show_frame("LoginPage")).pack(pady=20)

    def on_show(self, data=None):
        if CURRENT_USER and CURRENT_USER['role'] == 'admin':
            self.welcome_label.config(text=f"Admin Panel - Welcome, {CURRENT_USER['username']}")
        else:
            self.controller.show_frame("LoginPage") # Redirect if not admin

    def view_all_bookings_console(self):
        # This is a console output using tabulate as an example
        query = """
        SELECT b.booking_id, u.username, f.flight_number, f.origin, f.destination,
               b.booking_date, b.total_amount, b.status
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN flights f ON b.flight_id = f.flight_id
        ORDER BY b.booking_date DESC;
        """
        all_bookings = fetch_all(query)
        if all_bookings:
            headers = ["Booking ID", "User", "Flight No.", "Origin", "Dest.", "Date", "Amount", "Status"]
            print("\n--- All Bookings ---")
            print(tabulate(all_bookings, headers="keys", tablefmt="grid")) # "keys" uses dict keys as headers
            messagebox.showinfo("Admin Action", "All bookings printed to console.")
        else:
            messagebox.showinfo("Admin Action", "No bookings found.")

    def manage_flights_placeholder(self):
        messagebox.showinfo("Admin Action", "Flight management GUI is a future enhancement.\nAdmin could add/edit flights here.")


class BookFlightPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_flight_id = None
        self.selected_flight_details = None
        self.food_options_map = {} # To map display name to food_id

        tk.Label(self, text="Book a Flight", font=("Arial", 18, "bold")).pack(pady=10)

        # Search Criteria Frame
        search_frame = ttk.LabelFrame(self, text="Search Flights")
        search_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(search_frame, text="From:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.origin_entry = ttk.Entry(search_frame, width=20)
        self.origin_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(search_frame, text="To:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.dest_entry = ttk.Entry(search_frame, width=20)
        self.dest_entry.grid(row=0, column=3, padx=5, pady=5)

        # For simplicity, not adding date search, but it's important in a real system
        ttk.Button(search_frame, text="Search Flights", command=self.search_flights).grid(row=0, column=4, padx=10, pady=5)

        # Flights Display Frame (using Treeview)
        flights_frame = ttk.LabelFrame(self, text="Available Flights")
        flights_frame.pack(padx=10, pady=10, fill="both", expand=True)

        cols = ("Flight No", "Origin", "Destination", "Departure", "Arrival", "Eco Price", "Biz Price", "Eco Seats", "Biz Seats")
        self.flights_tree = ttk.Treeview(flights_frame, columns=cols, show='headings', selectmode="browse")
        for col in cols:
            self.flights_tree.heading(col, text=col)
            self.flights_tree.column(col, width=100, anchor="center") # Adjust width as needed
        self.flights_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(flights_frame, orient="vertical", command=self.flights_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.flights_tree.configure(yscrollcommand=scrollbar.set)

        self.flights_tree.bind("<<TreeviewSelect>>", self.on_flight_select)

        # Passenger Details Frame
        passenger_frame = ttk.LabelFrame(self, text="Passenger Details")
        passenger_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(passenger_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(passenger_frame, width=25)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(passenger_frame, text="Age:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.age_entry = ttk.Entry(passenger_frame, width=5)
        self.age_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(passenger_frame, text="Gender:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.gender_var = tk.StringVar(value="Male")
        self.gender_combo = ttk.Combobox(passenger_frame, textvariable=self.gender_var, values=["Male", "Female", "Other"], width=10, state="readonly")
        self.gender_combo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(passenger_frame, text="Class:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.class_var = tk.StringVar(value="Economy")
        self.class_combo = ttk.Combobox(passenger_frame, textvariable=self.class_var, values=["Economy", "Business"], width=10, state="readonly")
        self.class_combo.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(passenger_frame, text="Food Pref:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.food_var = tk.StringVar()
        self.food_combo = ttk.Combobox(passenger_frame, textvariable=self.food_var, width=25, state="readonly")
        self.food_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Action Buttons Frame
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)
        ttk.Button(action_frame, text="Confirm Booking", command=self.confirm_booking, style="Accent.TButton").pack(side="left", padx=10)
        ttk.Button(action_frame, text="Back to Dashboard", command=lambda: controller.show_frame("UserDashboardPage")).pack(side="left", padx=10)

    def on_show(self, data=None): # Refresh data when page is shown
        self.food_options_map = self.controller.get_food_options()
        self.food_combo['values'] = ["No Preference"] + list(self.food_options_map.keys())
        self.food_var.set("No Preference")
        self.search_flights() # Load all flights initially
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.selected_flight_id = None
        self.selected_flight_details = None

    def search_flights(self):
        for item in self.flights_tree.get_children(): # Clear previous results
            self.flights_tree.delete(item)

        origin = self.origin_entry.get().strip()
        destination = self.dest_entry.get().strip()

        query = """
        SELECT flight_id, flight_number, origin, destination, departure_time, arrival_time,
               economy_price, business_price,
               (economy_seats_total - economy_seats_booked) AS eco_avail,
               (business_seats_total - business_seats_booked) AS biz_avail
        FROM flights
        WHERE (economy_seats_total - economy_seats_booked) > 0 OR (business_seats_total - business_seats_booked) > 0
        """ # Only show flights with available seats
        params = []
        if origin:
            query += " AND origin LIKE %s"
            params.append(f"%{origin}%")
        if destination:
            query += " AND destination LIKE %s"
            params.append(f"%{destination}%")

        query += " ORDER BY departure_time"

        flights = fetch_all(query, tuple(params))
        if flights:
            for flight in flights:
                self.flights_tree.insert("", "end", iid=flight['flight_id'], values=(
                    flight['flight_number'], flight['origin'], flight['destination'],
                    flight['departure_time'].strftime('%Y-%m-%d %H:%M'),
                    flight['arrival_time'].strftime('%Y-%m-%d %H:%M'),
                    f"{flight['economy_price']:.2f}", f"{flight['business_price']:.2f}",
                    flight['eco_avail'], flight['biz_avail']
                ))
        else:
            messagebox.showinfo("No Flights", "No flights found matching your criteria.")

    def on_flight_select(self, event):
        selected_item = self.flights_tree.focus() # Get selected item's IID
        if selected_item:
            self.selected_flight_id = int(selected_item) # IID is flight_id
            # Fetch full flight details to use for booking if needed (e.g. prices)
            self.selected_flight_details = fetch_one("SELECT * FROM flights WHERE flight_id = %s", (self.selected_flight_id,))


    def confirm_booking(self):
        if not CURRENT_USER:
            messagebox.showerror("Error", "You must be logged in to book.")
            self.controller.show_frame("LoginPage")
            return

        if not self.selected_flight_id or not self.selected_flight_details:
            messagebox.showerror("Error", "Please select a flight first.")
            return

        name = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        gender = self.gender_var.get()
        seat_class = self.class_var.get()
        food_pref_display = self.food_var.get()

        food_id = None
        if food_pref_display != "No Preference":
            food_id = self.food_options_map.get(food_pref_display)

        if not name or not age_str:
            messagebox.showerror("Error", "Passenger name and age are required.")
            return
        try:
            age = int(age_str)
            if age <= 0: raise ValueError("Age must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid age.")
            return

        # Determine price and check seat availability
        price = 0
        available_seats = 0
        if seat_class == "Economy":
            price = self.selected_flight_details['economy_price']
            available_seats = self.selected_flight_details['economy_seats_total'] - self.selected_flight_details['economy_seats_booked']
        elif seat_class == "Business":
            price = self.selected_flight_details['business_price']
            available_seats = self.selected_flight_details['business_seats_total'] - self.selected_flight_details['business_seats_booked']

        if available_seats <= 0:
            messagebox.showerror("Sold Out", f"Sorry, {seat_class} class is sold out for this flight.")
            return

        # Create Booking
        booking_success, booking_id = execute_query(
            "INSERT INTO bookings (user_id, flight_id, total_amount) VALUES (%s, %s, %s)",
            (CURRENT_USER['user_id'], self.selected_flight_id, price)
        )

        if not booking_success or not booking_id:
            messagebox.showerror("Booking Error", "Failed to create booking record.")
            return

        # Add Passenger
        passenger_success, _ = execute_query(
            "INSERT INTO passengers (booking_id, passenger_name, age, gender, seat_class, food_preference_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (booking_id, name, age, gender, seat_class, food_id)
        )

        if not passenger_success:
            # Rollback booking (simple delete for this example, transaction preferred)
            execute_query("DELETE FROM bookings WHERE booking_id = %s", (booking_id,))
            messagebox.showerror("Booking Error", "Failed to add passenger. Booking cancelled.")
            return

        # Update flight seat count
        seat_update_column = "economy_seats_booked" if seat_class == "Economy" else "business_seats_booked"
        update_flight_success, _ = execute_query(
            f"UPDATE flights SET {seat_update_column} = {seat_update_column} + 1 WHERE flight_id = %s",
            (self.selected_flight_id,)
        )

        if not update_flight_success:
            # This is a critical error. Data inconsistency.
            # In a real system, you'd have more robust transaction handling.
            messagebox.showerror("Critical Error", "Failed to update flight seat count. Contact support.")
            # Consider trying to rollback passenger and booking here too.
            return

        # --- Invoice Generation (Simple Message Box) ---
        invoice_details = f"""
        --- FLIGHT BOOKING INVOICE ---
        Booking ID: {booking_id}
        Passenger Name: {name}
        Flight Number: {self.selected_flight_details['flight_number']}
        From: {self.selected_flight_details['origin']} To: {self.selected_flight_details['destination']}
        Departure: {self.selected_flight_details['departure_time'].strftime('%Y-%m-%d %H:%M')}
        Class: {seat_class}
        Food: {food_pref_display if food_pref_display != "No Preference" else "None"}
        ---------------------------------
        Total Amount: INR {price:.2f}
        Payment Status: PAID (Simulated)
        ---------------------------------
        Thank you for booking with us!
        """
        messagebox.showinfo("Booking Confirmed & Invoice", invoice_details)
        print(invoice_details) # Also print to console

        # Reset form and refresh flights
        self.name_entry.delete(0, tk.END)
        self.age_entry.delete(0, tk.END)
        self.selected_flight_id = None
        self.selected_flight_details = None
        self.search_flights() # Refresh flight list (to show updated seat counts)


class ViewAvailableFlightsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Available Flights Schedule", font=("Arial", 18, "bold")).pack(pady=10)

        # Frame for Treeview and Scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        cols = ("Flight No", "Origin", "Destination", "Departure", "Arrival", "Aircraft", "Eco Seats Avail.", "Biz Seats Avail.")
        self.flights_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            self.flights_tree.heading(col, text=col)
            self.flights_tree.column(col, width=120, anchor="w") # Adjust width

        self.flights_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.flights_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.flights_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(self, text="Refresh", command=self.load_flights).pack(pady=5)
        ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame("UserDashboardPage")).pack(pady=10)

    def on_show(self, data=None):
        self.load_flights()

    def load_flights(self):
        for item in self.flights_tree.get_children():
            self.flights_tree.delete(item)

        query = """
        SELECT flight_number, origin, destination, departure_time, arrival_time, aircraft_name,
               (economy_seats_total - economy_seats_booked) AS eco_available,
               (business_seats_total - business_seats_booked) AS biz_available
        FROM flights
        WHERE departure_time > NOW()
        ORDER BY departure_time;
        """
        flights_data = fetch_all(query)

        if flights_data:
            for flight in flights_data:
                self.flights_tree.insert("", "end", values=(
                    flight['flight_number'], flight['origin'], flight['destination'],
                    flight['departure_time'].strftime('%Y-%m-%d %H:%M'),
                    flight['arrival_time'].strftime('%Y-%m-%d %H:%M'),
                    flight['aircraft_name'],
                    flight['eco_available'], flight['biz_available']
                ))
        else:
            self.flights_tree.insert("", "end", values=("No upcoming flights found.", "", "", "", "", "", "", ""))


class ViewMyTicketsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="My Booked Tickets", font=("Arial", 18, "bold")).pack(pady=10)

        # Frame for Treeview and Scrollbar
        tree_frame = tk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        cols = ("Booking ID", "Flight No", "Origin", "Dest.", "Departure", "Passenger", "Age", "Class", "Food", "Status", "Total Amt")
        self.tickets_tree = ttk.Treeview(tree_frame, columns=cols, show='headings')
        for col in cols:
            self.tickets_tree.heading(col, text=col)
            self.tickets_tree.column(col, width=100, anchor="w")

        self.tickets_tree.column("Departure", width=140)
        self.tickets_tree.column("Total Amt", width=80, anchor="e")

        self.tickets_tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tickets_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tickets_tree.configure(yscrollcommand=scrollbar.set)

        ttk.Button(self, text="Refresh", command=self.load_my_tickets).pack(pady=5)
        ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame("UserDashboardPage")).pack(pady=10)

    def on_show(self, data=None):
        if not CURRENT_USER:
            self.controller.show_frame("LoginPage")
            return
        self.load_my_tickets()

    def load_my_tickets(self):
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)

        user_id = self.controller.get_current_user_id()
        if not user_id: return

        query = """
        SELECT
            b.booking_id,
            f.flight_number,
            f.origin,
            f.destination,
            f.departure_time,
            p.passenger_name,
            p.age,
            p.seat_class,
            COALESCE(fi.item_name, 'None') AS food_preference,
            b.status,
            b.total_amount
        FROM bookings b
        JOIN flights f ON b.flight_id = f.flight_id
        JOIN passengers p ON b.booking_id = p.booking_id
        LEFT JOIN food_items fi ON p.food_preference_id = fi.food_id
        WHERE b.user_id = %s
        ORDER BY f.departure_time DESC, b.booking_id;
        """
        tickets = fetch_all(query, (user_id,))

        if tickets:
            for ticket in tickets:
                self.tickets_tree.insert("", "end", iid=ticket['booking_id'], values=( # Use booking_id as iid
                    ticket['booking_id'], ticket['flight_number'], ticket['origin'], ticket['destination'],
                    ticket['departure_time'].strftime('%Y-%m-%d %H:%M'),
                    ticket['passenger_name'], ticket['age'], ticket['seat_class'],
                    ticket['food_preference'], ticket['status'], f"{ticket['total_amount']:.2f}"
                ))
        else:
            self.tickets_tree.insert("", "end", values=("No tickets booked yet.", "", "", "", "", "", "", "", "", "", ""))


class EditTicketPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_booking_id_to_edit = None
        self.food_options_map = {}

        tk.Label(self, text="Edit / Cancel Ticket", font=("Arial", 18, "bold")).pack(pady=10)

        # Input Frame for Booking ID
        input_frame = ttk.LabelFrame(self, text="Find Your Booking")
        input_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(input_frame, text="Enter Booking ID:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.booking_id_entry = ttk.Entry(input_frame, width=15)
        self.booking_id_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Fetch Details", command=self.fetch_booking_details).grid(row=0, column=2, padx=10, pady=5)

        # Details Display & Edit Frame (Initially hidden or disabled)
        self.details_frame = ttk.LabelFrame(self, text="Booking Details (Passenger Specific)")
        # self.details_frame.pack(padx=10, pady=10, fill="x") # Pack when details are loaded

        tk.Label(self.details_frame, text="Passenger Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_label = tk.Label(self.details_frame, text="-", width=25, anchor="w") # Display only
        self.name_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(self.details_frame, text="Flight:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.flight_label = tk.Label(self.details_frame, text="-", width=25, anchor="w") # Display only
        self.flight_label.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        tk.Label(self.details_frame, text="Change Food Pref:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.food_var = tk.StringVar()
        self.food_combo = ttk.Combobox(self.details_frame, textvariable=self.food_var, width=25, state="disabled")
        self.food_combo.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Action Buttons
        self.action_button_frame = tk.Frame(self) # Pack when details are loaded
        self.update_button = ttk.Button(self.action_button_frame, text="Update Food", command=self.update_food_preference, state="disabled")
        self.update_button.pack(side="left", padx=10, pady=10)
        self.cancel_button = ttk.Button(self.action_button_frame, text="Cancel Ticket", command=self.cancel_ticket, state="disabled", style="Cancel.TButton")
        self.cancel_button.pack(side="left", padx=10, pady=10)

        s = ttk.Style()
        s.configure("Cancel.TButton", foreground="white", background="red")


        ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame("UserDashboardPage")).pack(pady=20, side="bottom")

    def on_show(self, data=None):
        if not CURRENT_USER:
            self.controller.show_frame("LoginPage")
            return
        self.food_options_map = self.controller.get_food_options()
        self.food_combo['values'] = ["No Preference"] + list(self.food_options_map.keys())
        self.food_var.set("No Preference")
        self.reset_form()

    def reset_form(self):
        self.booking_id_entry.delete(0, tk.END)
        self.name_label.config(text="-")
        self.flight_label.config(text="-")
        self.food_var.set("No Preference")
        self.food_combo.config(state="disabled")
        self.update_button.config(state="disabled")
        self.cancel_button.config(state="disabled")
        self.current_booking_id_to_edit = None
        self.details_frame.pack_forget() # Hide frames
        self.action_button_frame.pack_forget()


    def fetch_booking_details(self):
        booking_id_str = self.booking_id_entry.get().strip()

        if not booking_id_str or not booking_id_str.isdigit():
            messagebox.showerror("Error", "Invalid Booking ID format.")
            return

        self.reset_form()  # Safe to reset now after getting the input

        booking_id = int(booking_id_str)
        user_id = self.controller.get_current_user_id()

        query = """
        SELECT
            p.passenger_id, p.passenger_name, p.food_preference_id,
            f.flight_number, f.origin, f.destination,
            b.status
        FROM passengers p
        JOIN bookings b ON p.booking_id = b.booking_id
        JOIN flights f ON b.flight_id = f.flight_id
        WHERE p.booking_id = %s AND b.user_id = %s;
        """
        passenger_details = fetch_one(query, (booking_id, user_id))

        if passenger_details:
            if passenger_details['status'] == 'Cancelled':
                messagebox.showinfo("Info", f"Booking ID {booking_id} is already cancelled.")
                self.name_label.config(text=passenger_details['passenger_name'])
                self.flight_label.config(text=f"{passenger_details['flight_number']} ({passenger_details['origin']}-{passenger_details['destination']})")
                self.details_frame.pack(padx=10, pady=10, fill="x")
                return

            self.current_booking_id_to_edit = booking_id
            self.current_passenger_id_to_edit = passenger_details['passenger_id']

            self.details_frame.pack(padx=10, pady=10, fill="x")
            self.action_button_frame.pack(pady=10)

            self.name_label.config(text=passenger_details['passenger_name'])
            self.flight_label.config(text=f"{passenger_details['flight_number']} ({passenger_details['origin']}-{passenger_details['destination']})")

            current_food_id = passenger_details['food_preference_id']
            current_food_name = "No Preference"
            if current_food_id:
                for name, id_val in self.food_options_map.items():
                    if id_val == current_food_id:
                        current_food_name = name
                        break
            self.food_var.set(current_food_name)

            self.food_combo.config(state="readonly")
            self.update_button.config(state="normal")
            self.cancel_button.config(state="normal")
        else:
            messagebox.showerror("Not Found", "Booking ID not found or does not belong to you.")
            self.reset_form()

    def update_food_preference(self):
        if not self.current_passenger_id_to_edit: return

        new_food_display = self.food_var.get()
        new_food_id = None
        if new_food_display != "No Preference":
            new_food_id = self.food_options_map.get(new_food_display)

        success, _ = execute_query(
            "UPDATE passengers SET food_preference_id = %s WHERE passenger_id = %s",
            (new_food_id, self.current_passenger_id_to_edit)
        )
        if success:
            messagebox.showinfo("Success", "Food preference updated successfully!")
            self.reset_form()
        else:
            messagebox.showerror("Error", "Failed to update food preference.")

    def cancel_ticket(self):
        if not self.current_booking_id_to_edit: return

        if not messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this ticket? This action cannot be undone."):
            return

        # Start a "transaction" manually (not true DB transaction here, but logical steps)
        conn = get_db_connection()
        if not conn: return
        cursor = conn.cursor()

        try:
            # 1. Get flight_id and seat_class for the booking to decrement seat count
            cursor.execute("""
                SELECT b.flight_id, p.seat_class
                FROM bookings b
                JOIN passengers p ON b.booking_id = p.booking_id
                WHERE b.booking_id = %s LIMIT 1;
            """, (self.current_booking_id_to_edit,)) # Assuming one passenger for simplicity
            flight_info = cursor.fetchone()

            if not flight_info:
                raise Exception("Could not retrieve flight info for seat decrement.")

            flight_id_to_update, seat_class_to_decrement = flight_info

            # 2. Update booking status
            cursor.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s", (self.current_booking_id_to_edit,))

            # 3. Decrement booked seat count on the flight
            # Note: This simple decrement assumes one passenger per booking ID for this operation.
            # A more complex system would count passengers for the booking_id.
            seat_column_to_decrement = "economy_seats_booked" if seat_class_to_decrement == "Economy" else "business_seats_booked"
            cursor.execute(
                f"UPDATE flights SET {seat_column_to_decrement} = GREATEST(0, {seat_column_to_decrement} - 1) WHERE flight_id = %s",
                (flight_id_to_update,)
            )

            conn.commit()
            messagebox.showinfo("Success", "Ticket cancelled successfully. Seat count updated.")
            self.reset_form()

        except mysql.connector.Error as err:
            conn.rollback()
            messagebox.showerror("Cancellation Error", f"Failed to cancel ticket: {err}")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Cancellation Error", f"An unexpected error occurred: {e}")
        finally:
            cursor.close()
            conn.close()


# --- App entry ---––--
if __name__ == "__main__":
    # Test DB Connection on startup
    conn_test = get_db_connection()
    if conn_test:
        conn_test.close()
        app = AirportApp()
        app.mainloop()
    else:
        print("Failed to connect to the database. Application will not start.")
        # Optionally, show a Tkinter root window with an error if GUI is partially initialized
        root_err = tk.Tk()
        root_err.withdraw() # Hide the main window
        messagebox.showerror("Fatal Error", "Cannot connect to the database. Please check configuration and MySQL server.")
        root_err.destroy()
