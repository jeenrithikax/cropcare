import sqlite3
import os

# ==============================
# CREATE DATABASE FOLDER
# ==============================
os.makedirs("database", exist_ok=True)

DB_PATH = "database/cropcare.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print("📦 Creating tables...")

# ==============================
# USERS TABLE
# ==============================
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
)
""")

# ==============================
# ADMIN TABLE
# ==============================
cur.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ==============================
# FEEDBACK TABLE
# ==============================
cur.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    feedback_type TEXT,
    message TEXT,
    image TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# ==============================
# SOIL DATA TABLE
# ==============================
cur.execute("""
CREATE TABLE IF NOT EXISTS soil_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    soil_type TEXT,
    nitrogen INTEGER,
    phosphorus INTEGER,
    potassium INTEGER,
    temperature REAL,
    humidity REAL,
    rainfall REAL,
    ph_min REAL,
    ph_max REAL
)
""")

# ==============================
# CROP DATA TABLE
# (pH based recommendation)
# ==============================
cur.execute("""
CREATE TABLE IF NOT EXISTS crop_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT,
    scientific_name TEXT,
    season TEXT,
    duration TEXT,
    demand TEXT,
    image TEXT,

    n_min INTEGER,
    n_max INTEGER,
    p_min INTEGER,
    p_max INTEGER,
    k_min INTEGER,
    k_max INTEGER,

    ph_min REAL,
    ph_max REAL,

    temp_min REAL,
    temp_max REAL,

    humidity_min REAL,
    humidity_max REAL,

    rainfall_min REAL,
    rainfall_max REAL
)
""")

print("✅ Tables created")

# ==============================
# INSERT DEFAULT ADMIN
# ==============================
cur.execute("""
INSERT OR IGNORE INTO admin (username, password)
VALUES (?, ?)
""", ("admin", "admin123"))

# ==============================
# INSERT SOIL DATA (Tamil Nadu)
# ==============================
cur.executemany("""
INSERT INTO soil_data
(location, soil_type, nitrogen, phosphorus, potassium,
 temperature, humidity, rainfall, ph_min, ph_max)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", [
    ("Ariyalur", "Red Soil", 260, 40, 160, 29, 60, 750, 6.0, 7.0),
("Chengalpattu", "Alluvial Soil", 300, 50, 210, 28, 65, 900, 6.5, 7.5),
("Chennai", "Alluvial Soil", 280, 45, 200, 30, 70, 850, 6.8, 7.8),
("Coimbatore", "Red Soil", 280, 45, 180, 26, 65, 700, 6.0, 7.0),
("Cuddalore", "Alluvial Soil", 310, 52, 220, 28, 68, 1000, 6.2, 7.6),
("Dharmapuri", "Red Soil", 250, 38, 150, 27, 55, 680, 5.8, 6.8),
("Dindigul", "Red Soil", 260, 40, 165, 29, 58, 720, 6.0, 7.0),
("Erode", "Alluvial Soil", 310, 52, 230, 28, 62, 780, 6.2, 7.8),
("Kallakurichi", "Red Soil", 255, 39, 155, 29, 60, 740, 6.0, 7.0),
("Kanchipuram", "Alluvial Soil", 300, 48, 210, 28, 67, 880, 6.4, 7.6),

("Kanyakumari", "Laterite Soil", 240, 35, 140, 27, 75, 1200, 5.5, 6.5),
("Karur", "Black Soil", 290, 48, 205, 30, 60, 760, 6.5, 8.0),
("Krishnagiri", "Red Soil", 250, 38, 150, 27, 58, 700, 5.8, 6.8),
("Madurai", "Red Soil", 260, 40, 160, 30, 55, 650, 6.0, 7.0),
("Mayiladuthurai", "Alluvial Soil", 305, 50, 215, 28, 70, 950, 6.5, 7.5),
("Nagapattinam", "Alluvial Soil", 320, 55, 230, 28, 75, 1100, 6.5, 7.8),
("Namakkal", "Black Soil", 285, 46, 200, 29, 60, 740, 6.5, 8.0),
("Nilgiris", "Laterite Soil", 230, 30, 130, 18, 80, 1400, 5.0, 6.0),
("Perambalur", "Red Soil", 255, 39, 155, 29, 60, 720, 6.0, 7.0),
("Pudukkottai", "Red Soil", 250, 38, 150, 30, 58, 700, 5.8, 6.8),

("Ramanathapuram", "Sandy Soil", 220, 30, 120, 32, 55, 600, 7.0, 8.5),
("Ranipet", "Red Soil", 265, 42, 170, 29, 62, 760, 6.2, 7.2),
("Salem", "Black Soil", 290, 48, 210, 29, 60, 720, 6.5, 8.2),
("Sivaganga", "Red Soil", 245, 36, 145, 30, 56, 680, 5.8, 6.8),
("Tenkasi", "Red Soil", 255, 39, 155, 29, 60, 750, 6.0, 7.0),
("Thanjavur", "Alluvial Soil", 320, 55, 220, 28, 70, 900, 6.5, 7.5),
("Theni", "Red Soil", 250, 38, 150, 27, 60, 800, 5.8, 6.8),
("Thoothukudi", "Sandy Soil", 225, 32, 130, 31, 58, 650, 7.0, 8.5),
("Tiruchirappalli", "Red Soil", 260, 40, 160, 29, 60, 750, 6.0, 7.0),

("Tirunelveli", "Red Soil", 250, 38, 150, 31, 58, 680, 5.8, 7.0),
("Tirupattur", "Red Soil", 255, 39, 155, 28, 60, 720, 6.0, 7.0),
("Tiruppur", "Black Soil", 285, 46, 200, 28, 60, 700, 6.5, 8.0),
("Tiruvallur", "Alluvial Soil", 300, 48, 210, 28, 68, 850, 6.4, 7.6),
("Tiruvannamalai", "Red Soil", 260, 40, 160, 29, 60, 760, 6.0, 7.0),
("Tiruvarur", "Alluvial Soil", 315, 54, 225, 28, 72, 1000, 6.5, 7.8),
("Vellore", "Red Soil", 265, 42, 170, 29, 62, 740, 6.2, 7.2),
("Viluppuram", "Laterite Soil", 240, 35, 140, 27, 68, 820, 5.5, 6.5),
("Virudhunagar", "Red Soil", 245, 36, 145, 31, 56, 670, 5.8, 6.8)

])

# ==============================
# COMMIT & CLOSE
# ==============================
conn.commit()
conn.close()

print("🎉 Database setup completed successfully!")
print("👉 Admin login: admin / admin123")
