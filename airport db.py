import mysql.connector as my_sql

def create_database():
    try:
        connection = my_sql.connect(
            host="localhost",
            user="root",
            password="123456"
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS airport_management;")
        print("✅ Database created or already exists.")
    except my_sql.Error as err:
        print(f"❌ Error while creating database: {err}")
    finally:
        cursor.close()
        connection.close()

def setup_tables_and_data():
    try:
        connection = my_sql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="airport_management"
        )
        cursor = connection.cursor()

        statements = [
            # Users table
            """CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                password VARCHAR(255) NOT NULL,
                phone_number VARCHAR(15) NOT NULL UNIQUE,
                role VARCHAR(10) DEFAULT 'user'
            );""",

            # Food items
            """CREATE TABLE IF NOT EXISTS food_items (
                food_id INT AUTO_INCREMENT PRIMARY KEY,
                item_name VARCHAR(100) NOT NULL,
                type ENUM('Veg', 'Non-Veg', 'Beverage') NOT NULL,
                price DECIMAL(10, 2) DEFAULT 0.00
            );""",

            # Flights
            """CREATE TABLE IF NOT EXISTS flights (
                flight_id INT AUTO_INCREMENT PRIMARY KEY,
                flight_number VARCHAR(20) NOT NULL UNIQUE,
                origin VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                aircraft_name VARCHAR(100),
                economy_seats_total INT DEFAULT 100,
                economy_seats_booked INT DEFAULT 0,
                economy_price DECIMAL(10, 2) NOT NULL,
                business_seats_total INT DEFAULT 20,
                business_seats_booked INT DEFAULT 0,
                business_price DECIMAL(10, 2) NOT NULL
            );""",

            # Bookings
            """CREATE TABLE IF NOT EXISTS bookings (
                booking_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                flight_id INT NOT NULL,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                status VARCHAR(20) DEFAULT 'Confirmed',
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (flight_id) REFERENCES flights(flight_id)
            );""",

            # Passengers
            """CREATE TABLE IF NOT EXISTS passengers (
                passenger_id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id INT NOT NULL,
                passenger_name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                seat_class ENUM('Economy', 'Business') NOT NULL,
                food_preference_id INT,
                FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
                FOREIGN KEY (food_preference_id) REFERENCES food_items(food_id)
            );""",

            # Insert Admin
            """INSERT IGNORE INTO users (username, password, phone_number, role)
               VALUES ('admin', 'admin123', '0000000000', 'admin');""",

            # Insert Food Items
            """INSERT IGNORE INTO food_items (item_name, type, price) VALUES
               ('Vegetable Biryani', 'Veg', 5.00),
               ('Paneer Tikka Masala', 'Veg', 6.00),
               ('Dal Makhani with Rice', 'Veg', 5.50),
               ('Chicken Curry with Rice', 'Non-Veg', 7.00),
               ('Grilled Fish', 'Non-Veg', 8.00),
               ('Mutton Korma', 'Non-Veg', 7.50),
               ('Orange Juice', 'Beverage', 2.00),
               ('Coffee/Tea', 'Beverage', 1.50);""",

            # Insert Flights
            """INSERT IGNORE INTO flights (flight_number, origin, destination, departure_time, arrival_time, aircraft_name, economy_seats_total, economy_price, business_seats_total, business_price) VALUES
               ('AI201', 'Delhi', 'Mumbai', '2024-09-01 10:00:00', '2024-09-01 12:00:00', 'Boeing 737 (Eco Alpha)', 120, 5000.00, 20, 15000.00),
               ('SJ405', 'Mumbai', 'Bangalore', '2024-09-01 14:00:00', '2024-09-01 15:30:00', 'Airbus A320 (Eco Bravo)', 100, 4500.00, 15, 12000.00),
               ('UK880', 'Delhi', 'Bangalore', '2024-09-02 08:00:00', '2024-09-02 10:30:00', 'Boeing 777 (Biz Charlie)', 80, 7000.00, 30, 20000.00),
               ('6E555', 'Kolkata', 'Chennai', '2024-09-02 18:00:00', '2024-09-02 20:15:00', 'Airbus A321 (Eco Delta)', 150, 5500.00, 10, 16000.00),
               ('BA001', 'London', 'New York', '2024-09-03 11:00:00', '2024-09-03 14:00:00', 'Boeing 747 (Biz Eagle)', 50, 30000.00, 40, 75000.00),
               ('EK203', 'Dubai', 'London', '2024-09-03 15:00:00', '2024-09-03 19:30:00', 'Airbus A380 (Biz Foxtrot)', 70, 25000.00, 50, 60000.00),
               ('QF002', 'Sydney', 'Singapore', '2024-09-04 09:00:00', '2024-09-04 15:00:00', 'Boeing 787 (Eco Golf)', 110, 18000.00, 25, 40000.00),
               ('LH760', 'Frankfurt', 'Delhi', '2024-09-04 13:00:00', '2024-09-04 23:50:00', 'Airbus A350 (Eco Hotel)', 130, 22000.00, 20, 50000.00);"""
        ]

        for stmt in statements:
            cursor.execute(stmt)

        connection.commit()
        print(" Tables created and sample data inserted successfully.")

    except my_sql.Error as err:
        print(f" Error while setting up tables: {err}")
    finally:
        cursor.close()
        connection.close()

# Execute both steps
create_database()
setup_tables_and_data()
