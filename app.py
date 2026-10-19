from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for

import automation
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

SERVICES = ["Web Development", "Mobile App", "SEO / Marketing", "UI/UX Design", "Consultancy", "Other"]


@app.route("/")
def index():
    return render_template("index.html", services=SERVICES, app_name=config.APP_NAME)


@app.route("/submit", methods=["POST"])
def submit():
    data = {k: request.form.get(k, "").strip() for k in ("name", "email", "phone", "company", "service", "message")}
    if not data["name"] or not data["email"] or not data["message"]:
        return render_template("index.html", services=SERVICES, app_name=config.APP_NAME,
                               error="Name, email aur message required hain."), 400
    record = automation.save_submission(data)
    automation.run_pipeline(record)
    return redirect(url_for("thanks", rid=record["id"]))


@app.route("/thanks/<int:rid>")
def thanks(rid):
    return render_template("thanks.html", rid=rid, app_name=config.APP_NAME)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", app_name=config.APP_NAME,
                           demo=config.DEMO_MODE)


@app.route("/api/stats")
def api_stats():
    rows = automation.load_submissions()
    logs = automation.load_logs()
    today = rows[-1]["timestamp"][:10] if rows else ""
    today_count = sum(1 for r in rows if r["timestamp"][:10] == today)
    services = {}
    for r in rows:
        s = r["service"] or "Other"
        services[s] = services.get(s, 0) + 1
    return jsonify({
        "total": len(rows),
        "today": today_count,
        "emails_sent": sum(1 for r in rows if r["email_status"] == "sent"),
        "demo_emails": sum(1 for r in rows if r["email_status"] == "demo"),
        "failed": sum(1 for r in rows if r["email_status"] == "failed"),
        "logs": len(logs),
        "services": services,
    })


@app.route("/api/submissions")
def api_submissions():
    return jsonify(list(reversed(automation.load_submissions())))


@app.route("/api/logs")
def api_logs():
    return jsonify(list(reversed(automation.load_logs()))[:50])


@app.route("/export")
def export():
    automation._sync_excel()
    return send_file(config.SUBMISSIONS_XLSX, as_attachment=True, download_name="submissions.xlsx")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
