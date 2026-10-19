# AutoFlow

**Workflow Automation Tool** — Form submission se le kar auto reply tak, sab kuch automate.

International-level animated dashboard ke saath, company leads ko instantly capture, notify aur track karne ke liye.

## Features

- **Lead Capture Form** — modern glassmorphism UI with animations
- **Auto Save** — har submission CSV + Excel (`openpyxl`) me automatically save
- **Auto Reply Email** — customer ko turant branded confirmation email (SMTP)
- **Owner Notification** — new lead ki details owner ke inbox me
- **Live Dashboard** — animated stats, leads by service chart, automation log
- **Excel Export** — one click me poora data download

## Tech Stack

- Python 3 + Flask
- CSV + OpenPyXL (Excel)
- smtplib (SMTP email)
- Vanilla HTML/CSS/JS (animated UI)

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

- Form: http://127.0.0.1:5000/
- Dashboard: http://127.0.0.1:5000/dashboard
- Excel Export: http://127.0.0.1:5000/export

## Live Email Setup (Optional)

Demo mode me bina email ke chalta hai. Asli emails ke liye environment variables set karein:

```powershell
$env:SMTP_USER="aapka@gmail.com"
$env:SMTP_PASS="your-app-password"      # myaccount.google.com/apppasswords
$env:OWNER_EMAIL="owner@company.com"
python app.py
```

> App password kabhi code me hardcode na karein aur repo me commit na karein.

## Project Structure

```
app.py          # Flask routes + API
automation.py   # Pipeline: save -> auto reply -> notify -> logs
config.py       # Settings (env variables)
templates/      # Form, thank-you, dashboard
static/         # CSS + JS animations
data/           # submissions.csv / .xlsx, logs.csv (auto-created)
```

## License

MIT
