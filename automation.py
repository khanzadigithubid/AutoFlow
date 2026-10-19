import csv
import os
import smtplib
import threading
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config

HEADERS = ["id", "timestamp", "name", "email", "phone", "company", "service", "message", "email_status", "notify_status"]

_lock = threading.Lock()


def _ensure_files():
    os.makedirs(config.DATA_DIR, exist_ok=True)
    if not os.path.exists(config.SUBMISSIONS_CSV):
        with open(config.SUBMISSIONS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(HEADERS)


def log_action(action, status, detail=""):
    os.makedirs(config.DATA_DIR, exist_ok=True)
    new_file = not os.path.exists(config.LOGS_CSV)
    with open(config.LOGS_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "action", "status", "detail"])
        w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, status, detail])


def load_submissions():
    _ensure_files()
    with open(config.SUBMISSIONS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_logs():
    if not os.path.exists(config.LOGS_CSV):
        return []
    with open(config.LOGS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def next_id(rows):
    try:
        return max(int(r["id"]) for r in rows) + 1
    except (ValueError, KeyError):
        return 1


def save_submission(data):
    _ensure_files()
    with _lock:
        rows = load_submissions()
        rid = next_id(rows)
        record = {
            "id": rid,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": data.get("name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "company": data.get("company", ""),
            "service": data.get("service", ""),
            "message": data.get("message", ""),
            "email_status": "pending",
            "notify_status": "pending",
        }
        with open(config.SUBMISSIONS_CSV, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([record[h] for h in HEADERS])
    _sync_excel()
    log_action("form_received", "success", f"ID #{rid} - {record['name']}")
    return record


def update_status(rid, field, status):
    with _lock:
        rows = load_submissions()
        for r in rows:
            if str(r["id"]) == str(rid):
                r[field] = status
        with open(config.SUBMISSIONS_CSV, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=HEADERS)
            w.writeheader()
            w.writerows(rows)
    _sync_excel()


def _sync_excel():
    try:
        from openpyxl import Workbook
    except ImportError:
        return
    rows = load_submissions()
    wb = Workbook()
    ws = wb.active
    ws.title = "Submissions"
    ws.append([h.replace("_", " ").title() for h in HEADERS])
    for r in rows:
        ws.append([r.get(h, "") for h in HEADERS])
    wb.save(config.SUBMISSIONS_XLSX)


def _send(to_addr, subject, html_body):
    if config.DEMO_MODE:
        log_action("email_skipped", "demo", f"To: {to_addr} | {subject}")
        return "demo"
    msg = MIMEMultipart("alternative")
    msg["From"] = config.MAIL_FROM
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=20) as s:
        s.starttls()
        s.login(config.SMTP_USER, config.SMTP_PASS)
        s.sendmail(config.MAIL_FROM, [to_addr], msg.as_string())
    return "sent"


def _reply_template(rec):
    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;background:#f4f6fb;padding:30px">
      <div style="max-width:560px;margin:auto;background:#fff;border-radius:14px;overflow:hidden;
                  box-shadow:0 8px 30px rgba(0,0,0,.08)">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:26px 30px">
          <h2 style="margin:0;color:#fff">{config.APP_NAME}</h2>
          <p style="margin:6px 0 0;color:#e0e7ff">Thank you - we received your request</p>
        </div>
        <div style="padding:26px 30px;color:#334155;line-height:1.7">
          <p>Hi <b>{rec['name']}</b>,</p>
          <p>Thank you for contacting us. Your request has been logged and our team will
             reach out within 24 hours.</p>
          <table style="width:100%;font-size:14px;border-collapse:collapse">
            <tr><td style="padding:6px;color:#64748b">Reference</td><td><b>#{rec['id']}</b></td></tr>
            <tr><td style="padding:6px;color:#64748b">Service</td><td>{rec['service'] or '-'}</td></tr>
            <tr><td style="padding:6px;color:#64748b">Date</td><td>{rec['timestamp']}</td></tr>
          </table>
        </div>
        <div style="background:#f8fafc;padding:16px 30px;font-size:12px;color:#94a3b8">
          This is an automated confirmation from {config.APP_NAME}.
        </div>
      </div>
    </div>"""


def _notify_template(rec):
    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;background:#f4f6fb;padding:24px">
      <div style="max-width:600px;margin:auto;background:#fff;border-radius:12px;padding:24px">
        <h2 style="margin-top:0;color:#6366f1">New Lead #{rec['id']}</h2>
        <p><b>Name:</b> {rec['name']}<br>
           <b>Email:</b> {rec['email']}<br>
           <b>Phone:</b> {rec['phone'] or '-'}<br>
           <b>Company:</b> {rec['company'] or '-'}<br>
           <b>Service:</b> {rec['service'] or '-'}</p>
        <p style="background:#f8fafc;padding:14px;border-radius:8px">{rec['message']}</p>
      </div>
    </div>"""


def send_auto_reply(rec):
    if not rec.get("email"):
        update_status(rec["id"], "email_status", "skipped")
        return
    try:
        status = _send(rec["email"], f"{config.APP_NAME}: We received your request (#{rec['id']})",
                       _reply_template(rec))
        update_status(rec["id"], "email_status", status)
        log_action("auto_reply", status, f"ID #{rec['id']} -> {rec['email']}")
    except Exception as e:
        update_status(rec["id"], "email_status", "failed")
        log_action("auto_reply", "failed", f"ID #{rec['id']} -> {e}")


def notify_owner(rec):
    if not config.OWNER_EMAIL:
        update_status(rec["id"], "notify_status", "skipped")
        return
    try:
        status = _send(config.OWNER_EMAIL, f"New Lead #{rec['id']}: {rec['name']}", _notify_template(rec))
        update_status(rec["id"], "notify_status", status)
        log_action("owner_notify", status, f"ID #{rec['id']} -> {config.OWNER_EMAIL}")
    except Exception as e:
        update_status(rec["id"], "notify_status", "failed")
        log_action("owner_notify", "failed", f"ID #{rec['id']} -> {e}")


def run_pipeline(record):
    threading.Thread(target=send_auto_reply, args=(record,), daemon=True).start()
    threading.Thread(target=notify_owner, args=(record,), daemon=True).start()
