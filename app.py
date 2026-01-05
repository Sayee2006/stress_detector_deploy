from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///stress.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

IST = pytz.timezone("Asia/Kolkata")

# ================= DATABASE =================
class StressRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stress = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))

with app.app_context():
    db.create_all()

# ================= ROUTES =================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/history")
def history():
    records = StressRecord.query.order_by(StressRecord.created_at.desc()).limit(20).all()
    return render_template("history.html", records=records)

@app.route("/settings")
def settings():
    return render_template("settings.html")

# ================= STRESS PREDICTION =================
@app.route("/predict", methods=["POST"])
@app.route("/predict", methods=["POST"])
def predict():
    """
    STRICT rule-based stress detection
    NO averaging dilution
    """

    import random

    # ---- Simulated signals (later replaced by MediaPipe) ----
    smile_score = random.uniform(0.0, 1.0)     # >0.6 means smiling
    blink_rate = random.uniform(0.1, 2.0)      # blinks/sec
    tension_score = random.uniform(0.0, 1.0)   # jaw + stillness

    # ---- PRIORITY RULES ----

    # 😰 HIGH BLINKING → VERY HIGH STRESS
    if blink_rate >= 1.2:
        stress = random.randint(85, 100)

    # 😐 NOT SMILING + TENSE → HIGH STRESS
    elif smile_score < 0.4 and tension_score >= 0.6:
        stress = random.randint(70, 80)

    # 😊 SMILING → LOW STRESS
    elif smile_score >= 0.6:
        stress = random.randint(20, 40)

    # 😌 NEUTRAL CALM
    else:
        stress = random.randint(40, 50)

    return jsonify({"stress": stress})

# ================= SAVE RESULT =================
@app.route("/save_today", methods=["POST"])
def save_today():
    stress = request.json.get("stress")
    if stress is None:
        return jsonify({"message": "No stress data"}), 400

    record = StressRecord(stress=stress)
    db.session.add(record)
    db.session.commit()

    return jsonify({"message": "Stress saved successfully"})

# ================= STATS =================
@app.route("/stats")
def stats():
    records = StressRecord.query.all()

    if not records:
        return jsonify({
            "avg": "--",
            "last": "--",
            "streak": 0
        })

    avg = round(sum(r.stress for r in records) / len(records))
    last = records[-1].created_at.strftime("%d-%m-%Y %I:%M %p")

    return jsonify({
        "avg": avg,
        "last": last,
        "streak": 0
    })

if __name__ == "__main__":
    app.run(debug=True)
