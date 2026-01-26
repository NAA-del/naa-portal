
---

# Nigerian Academy of Audiology (NAA) Portal

**Version:** January 2026
**Status:** Active Development / Production Deployment
**Maintainer:** Nigerian Academy of Audiology

---

## 📌 Overview

The **Nigerian Academy of Audiology (NAA) Portal** is a comprehensive, cloud-based professional ecosystem designed to serve Audiologists, students, and affiliates across Nigeria.

The platform functions as:

* A **professional membership management system**
* A **CPD (Continuing Professional Development) portfolio tracker**
* A **tier-gated resource and document library**
* A **student academic and community hub**
* A **public-facing authority website for Audiology education and advocacy**

Built with scalability, governance, and professional branding in mind, the portal establishes the NAA as a centralized digital authority for Audiology practice in Nigeria.

---

## 🌍 Live Deployment

**Live Demo (Render):**
The NAA Portal is deployed on Render for development and staging purposes.

> ⚠️ *Note: Render free-tier limitations apply (cold starts).*

---

## 🚀 Core Features

### 1. Tiered Membership & Digital Identity System

The portal implements a role-based identity system where **UI design, access control, and privileges are determined by membership tier**.

**Membership Tiers:**

* **Fellow (FNAA)** – Executive-level members
  *Gold & Navy themed interface*
* **Full Member** – Licensed clinical practitioners
  *Professional Navy theme*
* **Associate Member** – Allied or affiliated professionals
  *Silver theme*
* **Student Member** – University chapter members
  *Teal academic-focused theme*

**Identity Features:**

* Automatic tier recognition system-wide
* Membership-specific dashboards
* Secure digital ID card unlocking after verification
* AI-powered face-centering for profile images using **Cloudinary Facial Detection**

---

### 2. Tier-Gated Resource Library

A centralized document and knowledge repository with strict professional access control.

**Access Levels:**

* Public
* Student
* Associate
* Full
* Fellow

**Behavior:**

* Members can access resources **at their tier and all tiers below**
* Sensitive documents remain hidden until admin verification
* Automatic filtering based on user role (no manual sorting required)

---

### 3. CPD Portfolio & Point Tracker

A complete Continuing Professional Development (CPD) management system.

**Features:**

* Logging of conferences, workshops, research, and trainings
* Secure certificate uploads (Cloudinary-backed)
* Annual CPD point calculation (e.g., 30-point yearly target)
* Admin verification workflow
* Bulk approval actions for efficiency

---

### 4. Student Community Hub

A national-scale academic network for Audiology students.

**Capabilities:**

* University-based student statistics
* Institution-specific announcements
* Academic resource sharing
* Inter-school collaboration and visibility

---

### 5. Custom Academy CMS (Admin Interface)

The Django Admin interface has been fully rebranded and extended.

**Enhancements:**

* Complete replacement of default Django branding with NAA identity
* Bulk verification of members and CPD records
* Resource upload interface with access-level assignment
* Engagement tracking via last-login monitoring

---

### 6. Public Authority & Content Platform (SEO-Focused)

The portal also functions as a **public Audiology authority website**.

**Key Components:**

* Custom-built Articles CMS
* Draft → Review → Publish editorial workflow
* CKEditor 5 with extended toolbar for professional writing
* Search-engine optimized public content
* Verified Members can submit journal-grade articles

---

## 🛠 Technology Stack

### Backend

* **Django 6.0**
* Django REST Framework
* PostgreSQL (Production)
* SQLite (Local Development)

### Frontend / UI

* Bootstrap 5
* Medicio Professional Theme
* FontAwesome
* Bootstrap Icons

### Storage & Media

* Cloudinary (media storage & AI image processing)

### Deployment & Infrastructure

* Render
* Gunicorn (WSGI server)
* WhiteNoise (static file serving)
* Automated `build.sh` pipeline

---

## 📁 Project Structure

```text
naa-portal/
│
├── accounts/          # Core business logic (models, views, forms)
├── naa_site/          # Project settings and configuration
├── templates/         # UI templates
├── static/            # Logos, PDFs, theme assets
├── staticfiles/       # Collected static files (production)
│
├── build.sh           # Render deployment automation
├── manage.py
├── requirements.txt
└── README.md
```

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`.

Key packages include:

* Django 6.0
* django-ckeditor-5
* django-cloudinary-storage
* djangorestframework
* gunicorn
* psycopg2-binary
* whitenoise
* SendGrid integration
* Cryptography & security libraries

---

## 🔧 Local Installation & Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd naa-portal
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin User

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

---

## 🔐 Environment Variables

Set the following environment variables via a `.env` file or hosting dashboard:

```text
SECRET_KEY
CLOUDINARY_URL
DATABASE_URL
EMAIL_USER
EMAIL_PASSWORD
```

---

## ☁ Deployment (Render)

**Build Command**

```bash
./build.sh
```

**Start Command**

```bash
python manage.py migrate --no-input && gunicorn naa_site.wsgi:application
```

**Notes:**

* WhiteNoise handles static file serving
* PostgreSQL is required in production
* Render free tier may sleep after inactivity

---

## 🧑‍💼 Administrative Workflow

### Member Verification

1. Review registration
2. Toggle `is_verified`
3. Member gains full access and digital ID

### Resource Management

1. Upload document
2. Assign access level
3. Resource becomes visible only to permitted tiers

### CPD Oversight

1. Review uploaded certificates
2. Bulk verify records
3. CPD points are automatically added

---

## 📅 Recent Updates (January 25, 2026)

### Platform Expansion

* Transitioned into a public Audiology authority hub
* Introduced SEO-friendly professional article system

### Governance Improvements

* Migrated “EXCO” role to **Admin**
* Added last-login engagement tracking
* Fixed dashboard logic issues

### Member Contributions

* Enabled verified member article submissions
* Integrated Cloudinary-backed article images

### Stability & Hardening

* Fixed production migration errors
* Resolved missing templates
* Improved URL routing for article content

---

## 📜 License & Ownership

© 2026 **Nigerian Academy of Audiology**
All rights reserved.

This software is proprietary and intended for official Academy use unless otherwise authorized.