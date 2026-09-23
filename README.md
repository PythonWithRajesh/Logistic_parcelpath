# 📦 ParcelPath Logistics — Enterprise Courier & Consignment Management System

[![Python Version](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django Version](https://img.shields.io/badge/Django-6.0+-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Razorpay](https://img.shields.io/badge/Payment-Razorpay%20Integrated-02042B?style=for-the-badge&logo=razorpay&logoColor=blue)](https://razorpay.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)]()

**ParcelPath Logistics** is a production-grade, full-stack logistics and shipment management web platform built with **Django** and **Bootstrap 5**. Designed to mirror the robust operational architectures of commercial logistics leaders (such as Delhivery, Shiprocket, and BlueDart), it delivers end-to-end parcel booking, automated QR waybills, dual payment processing (Razorpay + COD), real-time 5-stage telemetry tracking, downloadable PDF receipts, and a dedicated, mobile-friendly administration control panel.

---

## 🌟 Key Highlights & Features

### 🚚 Customer Portal
- **Realistic Commercial Homepage**:
  - Live consignment tracking simulation widget with quick demo lookup chips.
  - Interactive Freight Rate Estimator based on origin, destination, and package weight.
  - 3-step connected logistics roadmap, customer testimonials, and network guarantees.
- **Express Parcel Booking**:
  - Automated calculation of shipment cost based on parcel weight and category.
  - Generates a unique encrypted Tracking ID (`PP` + 8 alphanumeric digits) upon booking.
  - Dynamically renders and embeds a custom QR Code for fast warehouse scanning.
- **Dual Payment Processing**:
  - **Online Payment**: Integrated Razorpay checkout flow with instant signature verification and status capture.
  - **Cash on Delivery (COD)**: Doorstep cash settlement with automated pending invoice creation.
- **Real-Time 5-Stage Telemetry Tracking**:
  - Dynamic milestone tracking (`Parcel Booked` ➔ `Picked Up` ➔ `In Transit` ➔ `Out for Delivery` ➔ `Delivered` / `Cancelled`).
  - Pulsing live radar indicator on the currently active hub.
  - Case-insensitive search supporting both GET and POST requests.
- **Automated PDF Waybill & Invoicing**:
  - Direct PDF generation powered by **ReportLab** containing full consignment specs, sender/receiver details, barcodes, and digital stamps.
- **Services & Rate Calculator**:
  - Filterable catalog of express services (Same-Day Express, Air Freight, Surface Cargo, B2B Logistics).
  - Transit SLA comparison matrix and customer FAQ accordion.

### 🛡️ Custom Admin Control Center (`/custom_admin/`)
- **Operations & Business Telemetry**:
  - Live statistics: Active shipments, pending deliveries, completed drop-offs, and gross freight revenue.
- **Shipment Lifecycle Manager**:
  - Update shipment status in real time across the nationwide sortation network.
  - View full consignee profiles, waybill details, and attached QR tags.
- **100% Mobile-First Responsive Shell**:
  - Clean, distraction-free text-first navigation drawer with pure CSS hamburger toggle and dedicated close pill button.
  - Fixed bottom touch bar on mobile screens for rapid single-thumb navigation.
- **Customer Support Desk**:
  - Centralized inbox to view, manage, filter, and reply to customer inquiries and pickup requests.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend** | Python 3.13, Django 6.x |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, FontAwesome 6 |
| **Database** | SQLite (Default; readily swappable to PostgreSQL or MySQL) |
| **Payment Gateway** | Razorpay Python SDK |
| **Document Engine** | ReportLab (High-resolution PDF generation) |
| **Imaging & Barcodes** | Pillow (PIL), QRCode Generator |
| **Architecture** | Model-View-Template (MVT) Pattern |

---

## 📂 Project Architecture

```plaintext
logistics/
│
├── ParcelPath/                 # Main public portal application
│   ├── migrations/             # Database migrations
│   ├── models.py               # Book_parcel, Contact models
│   ├── views.py                # Booking, tracking, payments, PDF generator
│   ├── urls.py                 # Public route definitions
│   └── apps.py
│
├── custom_admin/               # Dedicated operations & admin panel
│   ├── migrations/             # Custom admin database migrations
│   ├── models.py               # Admin data schemas
│   ├── views.py                # Analytics dashboard, order & contact managers
│   ├── urls.py                 # Admin routes
│   └── templates/custom_admin/ # Admin HTML templates
│       ├── main.html           # Modern mobile-friendly admin base layout
│       ├── custom_dashboard.html # Operational metrics & charts
│       ├── cs_parcel.html      # Shipment management grid
│       └── ...
│
├── logistics/                  # Project configuration directory
│   ├── settings.py             # Global project settings & Razorpay keys
│   ├── urls.py                 # Root URL router
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/                  # Public frontend templates
│   ├── base.html               # Master layout (Navbar & Footer)
│   ├── home.html               # Enterprise landing page & rate estimator
│   ├── track_parcel.html       # Dynamic 5-stage consignment tracker
│   ├── book_parcel.html        # Parcel booking & quote form
│   ├── services.html           # Services catalog & comparison matrix
│   ├── contact.html            # Contact & inquiry desk
│   └── ...
│
├── static/                     # Static assets (CSS, JS, Logos, Vectors)
├── qr_codes/                   # Generated parcel QR codes
├── manage.py                   # Django execution utility
├── requirements.txt            # Python dependencies
└── .gitignore                  # Git ignore rules
```

---

## ⚡ Installation & Quick Start

Follow these simple steps to set up the project locally on your machine:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/parcelpath-logistics.git
cd parcelpath-logistics
```

### 2. Create and Activate a Virtual Environment
- **Windows (Command Prompt / PowerShell)**:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```
- **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables / Razorpay Keys
In `logistics/settings.py`, verify or set your Razorpay credentials:
```python
RAZORPAY_KEY_ID = 'your_test_key_id'
RAZORPAY_KEY_SECRET = 'your_test_key_secret'
```
*(You can get free test API keys from [Razorpay Dashboard](https://dashboard.razorpay.com))*

### 5. Apply Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 7. Launch Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Public Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Custom Admin Hub**: [http://127.0.0.1:8000/custom_admin/](http://127.0.0.1:8000/custom_admin/)
- **Django Standard Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🌐 Key URL Routing Reference

| Endpoint | Description |
| :--- | :--- |
| `/` or `/Home/` | Enterprise landing page with hero tracker and rate calculator |
| `/book_parcel/` | Express parcel booking form with weight-based freight quote |
| `/track_parcel/` | Real-time consignment telemetry tracker with dynamic milestones |
| `/services/` | Interactive logistics service catalog, pricing, and FAQ |
| `/contact/` | Customer inquiry submission form |
| `/payment-receipt/<tracking_id>/` | Download high-resolution official PDF payment receipt |
| `/custom_admin/` | Custom Admin Dashboard with shipment telemetry |
| `/custom_admin/cs_parcel/` | Admin shipment lifecycle & order management desk |
| `/custom_admin/cs_contact/` | Customer inquiry and communication desk |

---

## 🗄️ Database Models Overview

### `Book_parcel`
- **Sender & Consignee**: `sender_name`, `receiver_name`, `mobile_number`, `pickup_address`, `delivery_address`
- **Consignment Specs**: `parcel_weight`, `parcel_type`, `price`
- **Tracking & Telemetry**: `tracking_id` (Unique, auto-generated), `status` (`Parcel Booked`, `Picked Up`, `In Transit`, `Out for Delivery`, `Delivered`, `Cancelled`)
- **Payment & Gateway**: `payment_method` (`ONLINE`, `COD`), `payment_status` (`Paid`, `Pending`), `payment_id`, `order_id`
- **Scan Asset**: `qr_code` (Auto-generated `.png` asset uploaded to `qr_codes/`)

### `Contact`
- **Fields**: `name`, `email`, `mobile`, `date`, `message`

---

## 🚀 How to Push to GitHub

If you are uploading this repository to GitHub for the first time, execute the following commands in your project terminal:

```bash
# 1. Initialize git repository (if not already done)
git init

# 2. Add all files (respects .gitignore)
git add .

# 3. Commit your changes
git commit -m "feat: complete enterprise logistics platform with real-time tracking, payments, and admin panel"

# 4. Set main branch
git branch -M main

# 5. Link your remote GitHub repository
git remote add origin https://github.com/<your-github-username>/<your-repo-name>.git

# 6. Push to GitHub
git push -u origin main
```

---

## 📄 License
This project is open-source and licensed under the **MIT License**.

---

## 👨‍💻 Author & Acknowledgements
- **Developer**: Rajesh Lagdhir
- **Contact**: [rajeshlagdhir07@gmail.com](mailto:rajeshlagdhir07@gmail.com) | +91 72039 28160
- Built with ❤️ using **Django** & **Python**.
