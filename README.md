✈️ Airport Management System

A full-fledged Python-based Airport Management System using **Tkinter GUI**, **MySQL** database, and **modular architecture**. Designed for both **admin and user roles**, this system supports flight booking, food preferences, ticket editing, and invoice generation.

📌 Features

👤 User Side:
- User registration and login
- Book flights (Economy / Business)
- Select food preferences (Veg / Non-Veg / Beverages)
- View all booked tickets
- Edit or cancel bookings
- Download invoice (simulated)

👨‍✈️ Admin Side:
- Admin login
- View all bookings
- (Future scope) Add/edit flights

 🛠️ Technologies Used

| Tool           | Purpose                      |
|----------------|------------------------------|
| Python         | Core programming language    |
| Tkinter        | GUI framework (built-in)     |
| MySQL          | Relational database          |
| mysql-connector-python | Python-MySQL connector |
| tabulate       | Console tables (admin view)  |


⚙️ Setup Instructions

1. Clone the Repository

git clone https://github.com/URBANDUST/airportmanagement.git
cd airport-management-system


 2. Create and Activate Virtual Environment

 Windows
python -m venv venv
venv\Scripts\activate

 macOS/Linux
python3 -m venv venv
source venv/bin/activate


 3. Install Required Packages

pip install -r requirements.txt

 4. Start MySQL and Configure DB

- Open `airport db.py` and set your MySQL credentials (`host`, `user`, `password`).
- Run:

python "airport db.py"


This will create the database `airport_management` and populate it with sample data (flights and food items).

 5. Run the Application

python management.py

 📝 Admin Credentials


Phone Number: 0000000000
Password: admin12

📂 File Structure


├── airport db.py        # Database setup and sample data insertion
├── management.py        # Main application with GUI
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation

 🚀 Future Improvements
- Flight addition/edit GUI for admin
- Online payment integration
- QR code-based check-in system
- Email notifications

 Credits

Developed by **Dibya Ranjan Sahoo**  
Class 12 School Project

 📃 License

This project is for educational purposes and not intended for commercial use.
