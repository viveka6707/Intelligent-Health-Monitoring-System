from flask import Flask, render_template, request, redirect, session, jsonify, flash, send_file
import mysql.connector
from datetime import datetime
import pickle
import numpy as np
import os
import json
from io import BytesIO

# PDF Generation Libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.secret_key = "health_monitor_2026_key"

# ---------------- 1. DATABASE CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="health_db"
    )

# ---------------- 2. LOAD AI MODEL ----------------
try:
    model = pickle.load(open("risk_model.pkl", "rb"))
    label_encoder = pickle.load(open("label_encoder.pkl", "rb"))
    print("✅ AI Model Loaded Successfully")
except Exception as e:
    print(f"⚠️ Model Warning: {e}")
    model, label_encoder = None, None

# ----------------3. AUTHENTICATION (Login/Register) ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        db = get_db_connection()
        cursor = db.cursor(buffered=True)
        cursor.execute("SELECT id, username, profile_completed FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        db.close()
        if user:
            session['user_id'], session['username'] = user[0], user[1]
            return redirect("/dashboard") if user[2] == 1 else redirect("/complete_profile")
        flash("Invalid Credentials!", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO users(username, email, password, profile_completed) VALUES(%s,%s,%s,0)", 
                           (request.form['username'], request.form['email'], request.form['password']))
            db.commit()
            return redirect("/")
        except Exception as e: flash(f"Error: {e}", "danger")
        finally: db.close()
    return render_template("register.html")

# ---------------- 5. DASHBOARD & GRAPH DATA ----------------
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session: return redirect("/")
    db = get_db_connection()
    cursor = db.cursor(buffered=True)
    
    # User Profile Info
    cursor.execute("SELECT name, age, gender, emergency_contact FROM users WHERE id=%s", (session['user_id'],))
    u = cursor.fetchone()
    
    # Health Records for Table and Graph
    cursor.execute("SELECT temp, hr, sys_bp, dia_bp, disease, status, current_medicine, alt_medicine, oxygen_level, cough, headache, fatigue, nausea, date FROM records WHERE user_id=%s ORDER BY date DESC", (session['user_id'],))
    recs = cursor.fetchall()
    db.close()
    
    processed = []
    for r in recs:
        symptoms = []
        if r[9] == 1: symptoms.append("Cough")
        if r[10] == 1: symptoms.append("Headache")
        if r[11] == 1: symptoms.append("Fatigue")
        if r[12] == 1: symptoms.append("Nausea")
        processed.append({
            "temp": r[0], "hr": r[1], "sys_bp": r[2], "dia_bp": r[3],
            "disease": r[4], "status": r[5], "current_medicine": r[6],
            "alt_medicine": r[7], "oxygen_level": r[8], "symptoms": symptoms or ["None"],
            "date": r[13].strftime("%d-%m-%Y %H:%M")
        })
    
    # Graph-kku JSON data anuppugirom
    return render_template("dashboard.html", name=u[0], age=u[1], gender=u[2], emergency=u[3], records=processed, records_json=json.dumps(processed))

@app.route("/complete_profile", methods=["GET", "POST"])
def complete_profile():
    if 'user_id' not in session: return redirect("/")
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET name=%s, age=%s, gender=%s, emergency_contact=%s, profile_completed=1 WHERE id=%s", 
                       (request.form['name'], request.form['age'], request.form['gender'], request.form['emergency_contact'], session['user_id']))
        db.commit()
        db.close()
        return redirect("/dashboard")
    return render_template("complete_profile.html")

# ---------------- 6. ADD RECORD (Manual + AI Prediction) ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if 'user_id' not in session: return redirect("/")
    if request.method == "POST":
        try:
            temp = float(request.form['temperature'])
            hr = int(request.form['heart_rate'])
            bp_sys = float(request.form.get('bp_sys', 120))
            bp_dia = float(request.form.get('bp_dia', 80))
            oxygen = float(request.form.get('oxygen_level', 98))
            glucose = float(request.form.get('glucose', 95))
            cough = int(request.form.get('cough', 0))
            headache = int(request.form.get('headache', 0))
            fatigue = int(request.form.get('fatigue', 0))
            nausea = int(request.form.get('nausea', 0))
            
            db = get_db_connection()
            cursor = db.cursor(buffered=True)
            cursor.execute("SELECT age, gender FROM users WHERE id=%s", (session['user_id'],))
            u_info = cursor.fetchone()
            
            # Prediction Logical
            status, alerts = "Normal", []
            if temp > 37.5: alerts.append(f"Fever({temp}C)")
            if hr > 100 or hr < 60: alerts.append("Irregular HR")
            if oxygen < 95: alerts.append(f"Low Oxygen({oxygen}%)")
            if bp_sys >= 140 or bp_dia >= 90: alerts.append(f"High BP({int(bp_sys)}/{int(bp_dia)})")
            if glucose >= 126: alerts.append(f"High Glucose({glucose})")

            disease = "Healthy"
            if alerts:
                status = "Abnormal"
                gender_val = 1 if str(u_info[1]).strip().lower().startswith("m") else 0
                features = np.array([[u_info[0], gender_val, temp, hr, bp_sys, bp_dia, glucose, cough, headache, fatigue, nausea]])
                if model:
                    try:
                        disease = label_encoder.inverse_transform(model.predict(features))[0]
                    except Exception:
                        disease = "Healthy"
                if disease == "Healthy":
                    # Fallback rule-based mapping when the model is uncertain or cannot predict
                    if temp >= 38 and cough == 1:
                        disease = "Flu"
                    elif oxygen < 95 and cough == 1:
                        disease = "COVID-19"
                    elif oxygen < 95:
                        disease = "Pneumonia"
                    elif bp_sys >= 140 or bp_dia >= 90:
                        disease = "Hypertension"
                    elif temp > 37.5:
                        disease = "Fever"
                    elif hr > 100 or hr < 60:
                        disease = "Heart Disease"
                    elif glucose >= 126:
                        disease = "Diabetes"
                    else:
                        disease = "General Illness"

            alert_suggestions = []
            if temp > 37.5:
                alert_suggestions.append("Paracetamol 650mg every 4-6 hours + Rest")
            if hr > 100 or hr < 60:
                alert_suggestions.append("Consult cardiologist + beta-blocker (Atenolol/Metoprolol) if prescribed")
            if oxygen < 95:
                alert_suggestions.append("Oxygen support + Azithromycin + Ambroxol + Hydration")
            if bp_sys >= 140 or bp_dia >= 90:
                alert_suggestions.append("Amlodipine 5mg or Telmisartan 40mg daily + Low salt diet")
            if glucose >= 126:
                alert_suggestions.append("Metformin 500mg twice daily + Low-carb diet")
            if cough == 1:
                alert_suggestions.append("Dextromethorphan + Ambroxol + Warm fluids")
            if headache == 1:
                alert_suggestions.append("Ibuprofen 400mg or Paracetamol + Rest")
            if fatigue == 1:
                alert_suggestions.append("Hydration + Vitamin B complex + Rest")
            if nausea == 1:
                alert_suggestions.append("Bland diet + Antiemetic if needed")

            med_map = {
                "Hypertension": "Amlodipine (5mg) or Telmisartan (40mg) daily",
                "Fever": "Paracetamol 650mg or Ibuprofen 400mg every 4-6 hours + Rest",
                "Healthy": "No medicine needed - Healthy vitals! 🎉",
                "COVID-19": "Paracetamol/Ibuprofen + Vitamin D (2000 IU) + Rest + Hydration",
                "Flu": "Oseltamivir (Tamiflu) if within 48 hours + Paracetamol + Hydration",
                "Cold": "Cetirizine (Allergy) + Vitamin C 500mg + Honey + Rest",
                "Cough": "Dextromethorphan + Ambroxol + Honey + Warm water",
                "Diabetes": "Metformin 500mg twice daily with food + Balanced diet",
                "Thyroid": "Levothyroxine (Thyronorm) as per TSH levels + Regular monitoring",
                "Asthma": "Salbutamol (Asthalin) inhaler + Montelukast tablet",
                "COPD": "Salbutamol + Ipratropium inhaler + Breathing exercises",
                "Bronchitis": "Ambroxol + Dextromethorphan + Steam inhalation + Rest",
                "Pneumonia": "Azithromycin (500mg) + Ambroxol + Oxygen support if needed",
                "Heart Disease": "Aspirin 75mg + Atorvastatin + ACE inhibitors (Lisinopril)",
                "Anemia": "Iron tablets (Ferrous Sulfate 325mg) + Vitamin B12 (Cyanocobalamin)",
                "Migraine": "Ibuprofen 400mg + Paracetamol + Rest in dark room",
                "Allergy": "Cetirizine (Allergy) 10mg + Montelukast + Avoid triggers",
                "Anxiety": "Meditation + Deep breathing + Sertraline if severe (consult doctor)",
                "Insomnia": "Melatonin 3-5mg at bedtime + Regular sleep schedule",
                "Gastric": "Pantoprazole 40mg morning + Antacid (Gelusil) + Bland diet",
                "Diarrhea": "Loperamide (Imodium) + Oral rehydration solution + Bland food",
                "Constipation": "Fiber-rich diet + Psyllium husk + Increase water intake",
                "Acidity": "Omeprazole 20mg + Antacid + Avoid spicy food",
                "Arthritis": "Ibuprofen 400mg + Calcium + Vitamin D + Physiotherapy",
                "Back Pain": "Diclofenac 50mg + Muscle relaxant + Hot compress + Rest",
                "Kidney Disease": "Low sodium diet + Limit fluid + Lisinopril + Regular monitoring",
                "Liver Disease": "Silymarin (Milk Thistle) + Avoid alcohol + Protein-rich diet",
                "Obesity": "Regular exercise 30min + Balanced diet + Metformin if diabetic",
                "Tuberculosis": "RIPE therapy (Rifampin, Isoniazid, Pyrazinamide, Ethambutol) - Consult TB specialist"
            }
            if alert_suggestions:
                alt_med = ' | '.join(dict.fromkeys(alert_suggestions))
            else:
                alt_med = med_map.get(disease, "Multi-vitamin supplement + Hydration + Rest. Consult doctor for detailed diagnosis.")

            cursor.execute("INSERT INTO records (user_id, temp, hr, sys_bp, dia_bp, oxygen_level, current_medicine, disease, status, alt_medicine, cough, headache, fatigue, nausea, date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (session['user_id'], temp, hr, bp_sys, bp_dia, oxygen, request.form.get('current_medicine', 'none'), disease, status, alt_med, cough, headache, fatigue, nausea, datetime.now()))
            db.commit()
            db.close()
            return jsonify({"success": True, "status": status, "disease": disease, "alt_medicine": alt_med, "alerts": ", ".join(alerts) if alerts else "Vitals Normal"})
        except Exception as e: return jsonify({"success": False, "error": str(e)})
    return render_template("add_record.html")

# ---------------- 7. PDF REPORT GENERATION ----------------
@app.route("/download_report")
def download_report():
    if 'user_id' not in session: return redirect("/")
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT name, age FROM users WHERE id=%s", (session['user_id'],))
    u = cursor.fetchone()
    cursor.execute("SELECT date, temp, hr, oxygen_level, status FROM records WHERE user_id=%s ORDER BY date DESC", (session['user_id'],))
    recs = cursor.fetchall()
    db.close()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = [Paragraph(f"Health Monitoring Report: {u[0]}", getSampleStyleSheet()['Title']), Spacer(1, 15)]
    
    data = [["Date", "Time", "Temp", "HR", "O2%", "Status"]]
    for r in recs:
        data.append([r[0].strftime("%d-%m-%Y"), r[0].strftime("%H:%M:%S"), r[1], r[2], r[3], r[4]])
    
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.blue), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    return send_file(buffer, as_attachment=True, download_name=f"Report_{u[0]}_{timestamp}.pdf", mimetype='application/pdf')

# -------- 8. LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)