from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os
from werkzeug.utils import secure_filename
from datetime import datetime

# ======================================================
# APP CONFIG
# ======================================================
app = Flask(__name__)
app.secret_key = "cropcare_secret_key"

# ======================================================
# DATABASE
# ======================================================
DB_PATH = "database/cropcare.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ======================================================
# UPLOAD CONFIG
# ======================================================
CROP_UPLOAD = "static/uploads"
FEEDBACK_UPLOAD = "static/feedback_uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(CROP_UPLOAD, exist_ok=True)
os.makedirs(FEEDBACK_UPLOAD, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ======================================================
# AUTH HELPERS
# ======================================================
def user_logged_in():
    return "user" in session

def admin_logged_in():
    return session.get("admin_logged_in") is True

# ======================================================
# HOME
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")

# ======================================================
# USER REGISTER
# ======================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        e = request.form["email"]
        p = request.form["password"]
        c = request.form["confirm_password"]

        if p != c:
            return render_template("register.html", error="Passwords do not match")

        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username,email,password) VALUES (?,?,?)",
                (u, e, p)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template("register.html",
                                   error="Username or Email already exists")

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# ======================================================
# USER LOGIN
# ======================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = cur.fetchone()

        if not user:
            conn.close()
            return render_template("login.html", error="Invalid credentials")

        cur.execute(
            "UPDATE users SET last_login=? WHERE username=?",
            (datetime.now(), u)
        )
        conn.commit()
        conn.close()

        session.clear()
        session["user"] = u
        return redirect(url_for("dashboard"))

    return render_template("login.html")

# ======================================================
# USER DASHBOARD
# ======================================================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        username=session["user"]
    )

# ================= USER LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# =================RECOMMEND =====================
@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        location = request.form["location"]
        soil_type = request.form["soil_type"]
        soil_ph = float(request.form["soil_ph"])

        conn = get_db()
        cur = conn.cursor()

        # ---------- STEP 1: GET SOIL DATA ----------
        cur.execute("""
            SELECT
                nitrogen,
                phosphorus,
                potassium,
                temperature,
                humidity,
                rainfall
            FROM soil_data
            WHERE location = ?
              AND soil_type = ?
              AND ? BETWEEN ph_min AND ph_max
        """, (location, soil_type, soil_ph))

        soil = cur.fetchone()

        if not soil:
            conn.close()
            return render_template(
                "recommend.html",
                error="No soil data found for selected inputs",
                username=session["user"]
            )

        N = soil["nitrogen"]
        P = soil["phosphorus"]
        K = soil["potassium"]
        temp = soil["temperature"]
        hum = soil["humidity"]
        rain = soil["rainfall"]

        # ---------- STEP 2: FIND MATCHING CROP ----------
        cur.execute("""
            SELECT *
            FROM crop_data
            WHERE
                ? BETWEEN n_min AND n_max AND
                ? BETWEEN p_min AND p_max AND
                ? BETWEEN k_min AND k_max AND
                ? BETWEEN ph_min AND ph_max AND
                ? BETWEEN temp_min AND temp_max AND
                ? BETWEEN humidity_min AND humidity_max AND
                ? BETWEEN rainfall_min AND rainfall_max
            LIMIT 1
        """, (N, P, K, soil_ph, temp, hum, rain))

        crop = cur.fetchone()
        conn.close()

        if not crop:
            return render_template(
                "recommend.html",
                error="No suitable crop found for this soil",
                username=session["user"]
            )

        # ---------- STEP 3: SHOW CROP DETAILS ----------
        return render_template(
            "crop_details.html",
            crop=crop,
            N=N,
            P=P,
            K=K,
            temp=temp,
            hum=hum,
            rain=rain,
            soil_ph=soil_ph,
            location=location,
            soil_type=soil_type,
            username=session["user"]
        )

    return render_template(
        "recommend.html",
        username=session["user"]
    )



# ======================================================
# USER FEEDBACK
# ======================================================
@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if not user_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        ftype = request.form.get("type")
        msg = request.form.get("message")
        img = request.files.get("image")

        image_path = None

        if img and img.filename != "" and allowed_file(img.filename):
            filename = secure_filename(img.filename)

            # 🔥 UNIQUE NAME (avoid overwrite)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"

            save_path = os.path.join(FEEDBACK_UPLOAD, filename)
            img.save(save_path)

            # 👉 STORE RELATIVE PATH ONLY
            image_path = f"feedback_uploads/{filename}"

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO feedback (username, feedback_type, message, image)
            VALUES (?, ?, ?, ?)
        """, (session["user"], ftype, msg, image_path))
        conn.commit()
        conn.close()

        return render_template(
            "feedback.html",
            success="Feedback submitted successfully",
            username=session["user"]
        )

    return render_template("feedback.html", username=session["user"])

# ======================================================
# ADMIN LOGIN
# ======================================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (u, p))
        admin = cur.fetchone()
        conn.close()

        if not admin:
            return render_template("admin_login.html", error="Invalid admin")

        session.clear()
        session["admin_logged_in"] = True
        session["admin_username"] = u
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

# ======================================================
# ADMIN DASHBOARD
# ======================================================
@app.route("/admin/dashboard")
def admin_dashboard():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]
    conn.close()

    return render_template("admin_dashboard.html",
                           admin=session["admin_username"],
                           user_count=users)

# ======================================================
# ✅ ADMIN ADD CROP (IMPORTANT)
# ======================================================
@app.route("/admin/add-crop", methods=["GET", "POST"])
def admin_add_crop():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        img = request.files.get("image")

        if not img or not allowed_file(img.filename):
            return render_template("admin_add_crop.html",
                                   error="Upload valid image",
                                   admin=session["admin_username"])

        fname = secure_filename(img.filename)
        img.save(os.path.join(CROP_UPLOAD, fname))
        image_path = f"uploads/{fname}"

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO crop_data (
                crop_name, scientific_name, season, duration, demand, image,
                n_min, n_max, p_min, p_max, k_min, k_max,
                ph_min, ph_max, temp_min, temp_max,
                humidity_min, humidity_max, rainfall_min, rainfall_max
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            request.form["crop_name"],
            request.form["scientific_name"],
            request.form["season"],
            request.form["duration"],
            request.form["demand"],
            image_path,
            request.form["n_min"], request.form["n_max"],
            request.form["p_min"], request.form["p_max"],
            request.form["k_min"], request.form["k_max"],
            request.form["ph_min"], request.form["ph_max"],
            request.form["temp_min"], request.form["temp_max"],
            request.form["humidity_min"], request.form["humidity_max"],
            request.form["rainfall_min"], request.form["rainfall_max"]
        ))
        conn.commit()
        conn.close()

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_crop.html",
                           admin=session["admin_username"])

# ======================================================
# ADMIN VIEW USERS
# ======================================================
@app.route("/admin/users")
def admin_users():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT username,email,created_at,last_login
        FROM users ORDER BY created_at DESC
    """)
    users = cur.fetchall()
    conn.close()

    return render_template("admin_users.html",
                           users=users,
                           admin=session["admin_username"])

# ======================================================
# ADMIN VIEW FEEDBACK
# ======================================================
@app.route("/admin/feedback")
def admin_feedback_view():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    conn = get_db()
    feedbacks = conn.execute("""
        SELECT id, username, feedback_type, message, image, created_at
        FROM feedback
        ORDER BY id DESC
    """).fetchall()
    conn.close()

    return render_template(
        "admin_feedback.html",
        feedbacks=feedbacks,
        admin=session["admin_username"]
    )


# ======================================================
# ADMIN LOGOUT
# ======================================================
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("index"))

# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)
