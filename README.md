# Robotech NITK Member Proforma Generation System

Production-ready Django web application for automated **Member Proforma Generation**, credential assignment, QR token creation, and A4 PDF rendering for Robotech NITK.

---

## 1. System Architecture

```
Internet
   │
   ▼
Nginx Reverse Proxy (robotech.nitk.ac.in)
   │
   ├─► /                 ──► Existing Robotech Website
   │
   └─► /proforma/        ──► Django Application (127.0.0.1:8001)
         │
         ├── Gunicorn WSGI Server
         ├── PostgreSQL / SQLite Database
         ├── Pillow (Photo formatting)
         ├── WeasyPrint / ReportLab (A4 PDF Generation)
         └── QRCode Engine
```

---

## 2. Directory Structure

```
c:\Users\Adity\Desktop\Robotech\profile\
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── gunicorn.conf.py
├── robotech-proforma.service
├── nginx-proforma.conf
├── README.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── members/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py
│   ├── services/
│   │   ├── credentials.py
│   │   ├── qr.py
│   │   └── pdf.py
│   └── management/
│       └── commands/
│           └── seed_skills.py
├── templates/
│   ├── base.html
│   ├── 404.html
│   ├── 500.html
│   ├── members/
│   │   ├── form.html
│   │   ├── success.html
│   │   ├── member_detail.html
│   │   └── dashboard.html
│   └── pdf/
│       └── proforma_template.html
├── static/
├── media/
└── generated/
```

---

## 3. Deployment Instructions (Ubuntu Server)

### Step 1: System Package Prerequisites
Install Python 3, PostgreSQL, Nginx, and system dependencies required for PDF rendering (WeasyPrint / Cairo / Pango):

```bash
sudo apt update && sudo apt install -y \
    python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib libpq-dev \
    nginx build-essential \
    python3-cffi python3-brotli libpango-1.0-0 \
    libpangoft2-1.0-0 libharfbuzz-subset0 libffi-dev \
    libjpeg-dev zlib1g-dev libgdk-pixbuf2.0-0
```

---

### Step 2: Clone & Environment Setup

```bash
# Target directory
cd /var/www
sudo git clone <repository-url> robotech-proforma
cd robotech-proforma

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Configure Database & Environment

1. Create PostgreSQL database and user:
```bash
sudo -u postgres psql
```
```sql
CREATE DATABASE robotech_proforma;
CREATE USER robotech_user WITH PASSWORD 'secure_password_here';
ALTER ROLE robotech_user SET client_encoding TO 'utf8';
ALTER ROLE robotech_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE robotech_user SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE robotech_proforma TO robotech_user;
\q
```

2. Configure `.env` file:
```bash
cp .env.example .env
nano .env
```
Fill in production variables:
```env
SECRET_KEY=generate-a-strong-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=robotech.nitk.ac.in,127.0.0.1,localhost
FORCE_SCRIPT_NAME=/proforma

DB_ENGINE=django.db.backends.postgresql
DB_NAME=robotech_proforma
DB_USER=robotech_user
DB_PASSWORD=secure_password_here
DB_HOST=127.0.0.1
DB_PORT=5432

PROFORMA_DOMAIN=https://robotech.nitk.ac.in
```

---

### Step 4: Database Migrations & Static Files

```bash
source venv/bin/activate

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Seed pre-configured SIG skills
python manage.py seed_skills

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

---

### Step 5: Systemd Service Setup

```bash
# Copy service configuration
sudo cp robotech-proforma.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Start and enable service on boot
sudo systemctl start robotech-proforma
sudo systemctl enable robotech-proforma

# Check service status
sudo systemctl status robotech-proforma
```

---

### Step 6: Nginx Configuration

**Important:** Do NOT overwrite the main Nginx server block for `robotech.nitk.ac.in`. Simply append the required `/proforma/` location routes.

Edit the existing server configuration file (e.g. `/etc/nginx/sites-available/robotech`):

```nginx
# Add inside server { ... } block for robotech.nitk.ac.in:

location /proforma/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Script-Name /proforma;
    proxy_redirect off;
    client_max_body_size 10M;
}

location /proforma/static/ {
    alias /var/www/robotech-proforma/staticfiles/;
    expires 30d;
}

location /proforma/media/ {
    alias /var/www/robotech-proforma/media/;
    expires 7d;
}
```

Test and reload Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 4. Verification & Testing

Run the Django unit test suite:
```bash
python manage.py test
```

Access the application in your browser:
- Main Form: `https://robotech.nitk.ac.in/proforma/`
- Admin Dashboard: `https://robotech.nitk.ac.in/proforma/dashboard/`
- Django Admin: `https://robotech.nitk.ac.in/proforma/admin/`

---

## 5. Troubleshooting & Logs

- Gunicorn application logs: `/var/www/robotech-proforma/logs/proforma.log`
- Gunicorn stdout/stderr: `journalctl -u robotech-proforma -f`
- Nginx error logs: `tail -f /var/log/nginx/error.log`
