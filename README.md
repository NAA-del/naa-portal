# 🎓 Nigerian Academy of Audiology (NAA) Portal

[![Django](https://img.shields.io/badge/Django-6.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)](https://naa-portal.onrender.com)

**Version:** February 2026  
**Status:** Active Production  
**Maintainer:** Nigerian Academy of Audiology  
**Live URL:** [naa-portal.onrender.com](https://naa-portal.onrender.com)

---

## 📌 Overview

The **Nigerian Academy of Audiology (NAA) Portal** is a comprehensive, cloud-based professional ecosystem designed to serve audiologists, students, and affiliated professionals across Nigeria.

### What is the NAA Portal?

A unified digital platform that serves as:

- 🏛️ **Professional Membership Management System** - Multi-tier member registration and identity management
- 📚 **CPD Portfolio Tracker** - Continuing Professional Development point tracking and certification
- 📖 **Tier-Gated Resource Library** - Secure document repository with role-based access control
- 🎓 **Student Academic Hub** - National student community with university chapters
- 🌐 **Public Audiology Authority** - SEO-optimized content platform for advocacy and education
- 👥 **Committee Management System** - Organize and coordinate NAA committees
- 📰 **Announcement & Communication Center** - Multi-channel notification system

Built with **scalability**, **governance**, and **professional branding** in mind, the portal establishes NAA as the centralized digital authority for audiology practice in Nigeria.

---

## 🌍 Live Deployment

**Production URL:** [https://naa-portal.onrender.com](https://naa-portal.onrender.com)

**Hosting:** Render.com  
**Database:** PostgreSQL  
**Media Storage:** Cloudinary  
**Email Service:** SendGrid

> ⚠️ **Note:** Free tier may experience cold starts (30-60 seconds) after inactivity.

---

## ✨ Core Features

### 1. 🎫 Tiered Membership & Digital Identity

**Four-Tier Membership System:**

| Tier | Description | Access Level | Theme |
|------|-------------|--------------|-------|
| **Fellow (FNAA)** | Executive-level members | Full + Leadership | Gold & Navy |
| **Full Member** | Licensed clinical practitioners | Professional + CPD | Navy Blue |
| **Associate** | Allied or affiliated professionals | Professional | Silver |
| **Student** | University chapter members | Academic | Teal |

**Identity Features:**
- ✅ Automatic tier recognition system-wide
- ✅ Membership-specific dashboards
- ✅ Digital ID card (unlocked after admin verification)
- ✅ AI-powered profile image processing (Cloudinary facial detection)
- ✅ Verification badge display

### 2. 📚 Tier-Gated Resource Library

**Smart Access Control:**
- Members access resources at their tier + all lower tiers
- Automatic filtering based on authentication and membership level
- Secure file hosting via Cloudinary
- Categories: Academic, Clinical Guidelines, Research, Policy Documents

**Access Levels:**
```
Public → Student → Associate → Full → Fellow
  └── Everyone can see
           └── Students and above
                    └── Associates and above
                             └── Full members and above
                                      └── Fellows only
```

### 3. 📊 CPD Portfolio & Point Tracker

**Complete CPD Management:**
- 📝 Log conferences, workshops, research publications, training programs
- 📄 Secure certificate uploads (PDF validation)
- 🎯 Automatic point calculation (30-point annual target)
- ✅ Admin verification workflow
- 📈 Progress tracking with visual indicators
- 📊 Annual statistics and reporting

**CPD Categories:**
- Conferences & Workshops
- Research & Publications
- Clinical Training
- Online Courses
- Peer Review Activities

### 4. 🎓 Student Community Hub

**National Student Network:**
- 🏫 University-based student statistics
- 📢 Institution-specific announcements (All universities + targeted)
- 📚 Academic resource sharing
- 📈 Inter-school collaboration and visibility
- 🔗 Direct access to study materials and academic support

**Supported Universities:**
- University of Medical Sciences, Ondo (UNIMED)
- Federal University of Health Sciences, Ila-Orangun (FUHSI)
- Federal University of Health Sciences, Azare (FUHSA)
- Federal University Dutsin-Ma, Katsina (FUDMA)

### 5. 👥 Committee Management System

**Organizational Structure:**
- Committee creation and member assignment
- Director-level access control
- Committee-specific announcements
- Member workspace for collaboration
- Committee-scoped resources and documents

**Built-in Committees:**
- Scientific Research Committee
- Education & Training Committee
- Public Relations Committee
- Finance Committee
- Ethics & Professional Standards

### 6. 🎨 Custom Academy CMS (Django Admin)

**Fully Branded Admin Interface:**
- 🏢 Complete NAA branding (colors, logo, nomenclature)
- ⚡ Bulk verification for members and CPD records
- 📤 Resource upload with access-level assignment
- 📊 Engagement tracking (last login monitoring)
- 🔍 Advanced search and filtering
- 📧 Integrated email template management

### 7. 📰 Public Content Platform

**SEO-Optimized Authority Website:**
- 📝 Professional article publishing system
- 🔄 Draft → Review → Publish workflow
- ✍️ CKEditor 5 with extended toolbar
- 🖼️ Image management via Cloudinary
- 🔍 Search engine optimization
- 📊 Author attribution for verified members

---

## 🛠 Technology Stack

### Backend Framework
```
Django 6.0
├── Django REST Framework (API endpoints)
├── Django Sites Framework (multi-domain support)
├── Custom User Model (extended authentication)
└── Role-based permissions system
```

### Database
```
Production:  PostgreSQL (Render managed)
Development: SQLite3
Features:    Connection pooling, health checks
```

### Frontend & UI
```
Theme:       Medicio Professional (Bootstrap 5)
Icons:       Bootstrap Icons + Font Awesome
JavaScript:  Vanilla JS + AOS (Animate On Scroll)
Editor:      CKEditor 5 (rich text editing)
```

### Storage & Media
```
Provider:    Cloudinary
Features:    - AI facial detection for profile images
             - Automatic image optimization
             - Secure file storage
             - Video support (future)
```

### Email & Communication
```
Provider:    SendGrid
Features:    - Transactional emails
             - Template management
             - Delivery tracking
             - Domain authentication (DKIM/SPF)
```

### Deployment Infrastructure
```
Platform:    Render.com
Web Server:  Gunicorn (WSGI)
Static:      WhiteNoise (compression + caching)
Build:       Automated via build.sh
SSL:         Automatic via Render
```

### Security & Performance
```
Security:    - HTTPS enforcement
             - HSTS headers
             - Secure cookies
             - CSRF protection
             - Rate limiting (django-ratelimit)
             - File upload validation

Performance: - Database query optimization (select_related, prefetch_related)
             - Static file compression (WhiteNoise)
             - Image CDN (Cloudinary)
             - Browser caching headers
```

---

## 📁 Project Structure

```
naa-portal/
│
├── accounts/                   # Main Django app
│   ├── migrations/            # Database migrations
│   ├── templates/             # HTML templates
│   │   └── accounts/
│   │       ├── base.html      # Base template with navigation
│   │       ├── home.html      # Homepage
│   │       ├── profile.html   # Member profile
│   │       ├── student_hub.html
│   │       ├── cpd_tracker.html
│   │       └── ...
│   ├── models.py              # Data models (User, Committee, Announcement, etc.)
│   ├── views.py               # View functions and logic
│   ├── forms.py               # Form classes
│   ├── admin.py               # Admin interface customization
│   ├── urls.py                # App-specific URL routing
│   ├── decorators.py          # Custom permission decorators
│   └── validators.py          # File upload validators
│
├── naa_site/                  # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration (future)
│
├── static/                    # Static assets (development)
│   ├── assets/               # Medicio theme files
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── vendor/
│   ├── images/               # NAA branding
│   │   └── logo.png
│   └── docs/                 # Public documents
│       └── constitution.pdf
│
├── staticfiles/              # Collected static files (production)
├── media/                    # User uploads (local development)
├── logs/                     # Application logs
│   ├── naa_portal.log
│   └── security.log
│
├── build.sh                  # Render deployment script
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── .gitignore
├── STYLE_GUIDE.md           # Code standards (create this)
└── README.md                # This file
```

---

## 📦 Key Dependencies

### Core Framework
```python
Django==6.0                          # Web framework
djangorestframework==3.16.1          # API framework
psycopg2-binary==2.9.11             # PostgreSQL adapter
gunicorn==23.0.0                    # WSGI HTTP server
```

### Storage & Media
```python
cloudinary==1.44.1                   # Cloud storage
django-cloudinary-storage==0.3.0     # Django integration
pillow==12.0.0                       # Image processing
```

### Content & Forms
```python
django-ckeditor-5==0.2.19           # Rich text editor
django-ratelimit==4.1.0             # Rate limiting
```

### Email & Communication
```python
django-sendgrid-v5==1.3.1           # SendGrid integration
sendgrid==6.12.5                    # SendGrid SDK
```

### Deployment & Performance
```python
dj-database-url==3.1.0              # Database URL parsing
whitenoise==6.11.0                  # Static file serving
cryptography==46.0.3                # Encryption utilities
```

**Full list:** See `requirements.txt`

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13+
- pip (Python package manager)
- PostgreSQL (production) or SQLite (development)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/NAA-del/naa-portal.git
cd naa-portal
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in project root:

```bash
# Core Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional for local SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Cloudinary (required for media uploads)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

# SendGrid (required for emails)
SENDGRID_API_KEY=SG.your-api-key-here
DEFAULT_FROM_EMAIL=nigerianacademyofaudiology@gmail.com

# Site Configuration
SITE_URL=http://localhost:8000
ADMIN_EMAIL=admin@example.com
```

### 5. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Create Required Groups

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group

# Create role groups
Group.objects.get_or_create(name='exco')
Group.objects.get_or_create(name='trustee')
Group.objects.get_or_create(name='committee_director')

exit()
```

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 🔐 Environment Variables (Production)

Set these in your Render dashboard:

### Required Variables
```bash
SECRET_KEY=strong-random-secret-key-generate-new
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/db  # Auto-set by Render
CLOUDINARY_URL=cloudinary://key:secret@cloud
SENDGRID_API_KEY=SG.xxx
```

### Recommended Variables
```bash
SITE_URL=https://naa-portal.onrender.com
DEFAULT_FROM_EMAIL=nigerianacademyofaudiology@gmail.com
ADMIN_EMAIL=nigerianacademyofaudiology@gmail.com
ALLOWED_HOSTS=naa-portal.onrender.com,localhost,127.0.0.1
```

---

## ☁️ Deployment (Render)

### Render Configuration

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn naa_site.wsgi:application
```

### build.sh Script

```bash
#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input --clear

# Run database migrations
python manage.py migrate --no-input
```

### Deployment Checklist

- [ ] All environment variables set in Render
- [ ] `DEBUG=False` in production
- [ ] Database migrations tested locally
- [ ] Static files collected successfully
- [ ] Cloudinary URL configured
- [ ] SendGrid API key active
- [ ] Custom domain configured (if applicable)
- [ ] SSL certificate active
- [ ] Admin superuser created

---

## 📱 Progressive Web App (PWA) & Offline Support

### Overview
- Adds a service worker served as a true root asset via WhiteNoise.
- Provides reliable offline fallback and modern caching tuned for Django navigation and authentication.

### Root Assets (served at “/”)
- Service worker: `/sw.js` → [root_assets/sw.js](file:///c:/Users/HP/Desktop/naa_project/root_assets/sw.js)
- Offline page: `/offline.html` → [root_assets/offline.html](file:///c:/Users/HP/Desktop/naa_project/root_assets/offline.html)

### Settings Integration (WhiteNoise Root)
```python
# naa_site/settings.py
ROOT_ASSETS_DIR = BASE_DIR / "root_assets"
WHITENOISE_ROOT = ROOT_ASSETS_DIR
```

### Registration (Silent, CSP‑friendly)
- Include the registration script in the base template:
```html
<!-- accounts/templates/accounts/base.html -->
<script src="{% static 'js/sw-register.js' %}"></script>
```
- Script lives at: [static/js/sw-register.js](file:///c:/Users/HP/Desktop/naa_project/static/js/sw-register.js)
- Registers `/sw.js` quietly with console logging only.

### Caching Strategy
- Navigation (HTML): Network‑first to avoid breaking auth/navigation.
- JavaScript: Network‑first to avoid stale interactivity.
- CSS: Network‑first to avoid stale UI styles.
- Images/Fonts/Other static: Stale‑While‑Revalidate at runtime.
- Cross‑origin requests: Bypassed entirely (e.g., Cloudinary/CDNs).
- Precache minimal UI shell: `/offline.html`, `/static/images/favicon_bg.png?v=2`, `/static/images/logo.png`.
- Versioned caches with cleanup on `activate`; bump `SW_VERSION` in `sw.js` for releases.

### Safe Testing
- Unregister old service workers:
```javascript
navigator.serviceWorker.getRegistrations()
  .then(rs => rs.forEach(r => r.unregister()));
```
- Clear caches:
```javascript
caches.keys().then(names => Promise.all(names.map(n => caches.delete(n))));
```
- Offline verification (Chrome DevTools):
  - Application → Service Workers → check active worker
  - Network → toggle “Offline” → navigate pages
  - Expect `/offline.html` for navigations and cached favicon/logo to display

### Render Deployment Notes
- Commit `root_assets/` and `static/js/sw-register.js`.
- No Django views needed for `/sw.js` and `/offline.html` (served via WhiteNoise root).
- When updating `sw.js`, bump `SW_VERSION` to invalidate old caches.
- Standard Render build runs `collectstatic`; root assets are served directly and don’t require collection.

---

## 🧑‍💼 Administrative Workflows

### Member Verification Process

1. **Review Registration**
   - Login to Django Admin
   - Navigate to Users
   - Filter by `is_verified=False`

2. **Verify Member**
   - Review member details
   - Toggle `is_verified` to True
   - Save

3. **Outcome**
   - Member receives verification email
   - Digital ID becomes accessible
   - Full resource access granted

### Resource Management

1. **Upload Document**
   - Admin → Resources → Add Resource
   - Upload file (PDF/DOCX/Image)
   - Set category and description

2. **Set Access Level**
   - Choose: Public, Student, Associate, Full, or Fellow
   - Resource becomes visible only to permitted tiers

3. **Organize**
   - Add to category
   - Tag with keywords
   - Set featured status (optional)

### CPD Record Management

1. **Review Submissions**
   - Admin → CPD Records
   - Filter by `verified=False`

2. **Bulk Verification**
   - Select multiple records
   - Actions → "Approve selected CPD records"
   - Points automatically added to member profiles

3. **Reject/Request Revision**
   - Add admin comment
   - Notify member via email

### Committee Administration

1. **Create Committee**
   - Admin → Committees → Add Committee
   - Set name, description, director

2. **Add Members**
   - Select committee
   - Add members via ManyToMany field

3. **Post Announcements**
   - Admin → Committee Announcements
   - Choose committee
   - Write announcement
   - Members see it in their dashboard

---

## 📅 Recent Updates

### February 2026
- ✅ Fixed static files configuration for Django 6.0
- ✅ Updated session management (7-day sessions)
- ✅ Improved template consistency (Medicio theme)
- ✅ Enhanced contact page UI/UX
- ✅ Added comprehensive code style guide
- ✅ Fixed rate limiting issues

### January 2026
- ✅ Platform expansion to public authority hub
- ✅ SEO-friendly article publishing system
- ✅ Migrated "EXCO" role to proper Admin system
- ✅ Added last-login engagement tracking
- ✅ Fixed production migration errors
- ✅ Enabled verified member article submissions
- ✅ Integrated Cloudinary for article images

### December 2025
- ✅ Initial launch of member portal
- ✅ CPD tracking system implementation
- ✅ Student hub with university chapters
- ✅ Tier-gated resource library
- ✅ Digital ID card system

---

## 🔒 Security Features

### Authentication & Authorization
- ✅ Custom user model with extended fields
- ✅ Role-based access control (RBAC)
- ✅ Email verification system
- ✅ Secure password hashing (Django defaults)
- ✅ Session management with secure cookies

### Data Protection
- ✅ HTTPS enforcement (production)
- ✅ HSTS headers (1-year)
- ✅ Secure cookie flags (HttpOnly, Secure, SameSite)
- ✅ CSRF protection
- ✅ XSS prevention headers
- ✅ Clickjacking protection (X-Frame-Options)

### File Upload Security
- ✅ File type validation (MIME type + magic bytes)
- ✅ File size limits (5MB images, 10MB PDFs)
- ✅ Filename sanitization
- ✅ Path traversal prevention
- ✅ Malware signature detection

### Rate Limiting
- ✅ Login attempts: 5 per minute
- ✅ Registration: 10 per hour
- ✅ API endpoints: 100 requests/hour (authenticated)
- ✅ Anonymous API: 10 requests/hour

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing Checklist

**Authentication:**
- [ ] Registration works
- [ ] Login/logout works
- [ ] Password reset works
- [ ] Email verification works

**Member Features:**
- [ ] Profile updates correctly
- [ ] Digital ID displays
- [ ] CPD submission works
- [ ] Resource access based on tier

**Admin Features:**
- [ ] Member verification works
- [ ] Bulk CPD approval works
- [ ] Resource upload works
- [ ] Committee management works

---

## 📊 Database Models

### Core Models

```python
User              # Extended Django User
Executive         # Leadership profiles
StudentProfile    # Student academic details
Committee         # NAA committees
Announcement      # National announcements
StudentAnnouncement  # Student-specific
CommitteeAnnouncement  # Committee-specific
Resource          # Document library
CPDRecord         # CPD tracking
Article           # Content platform
Notification      # In-app notifications
EmailUpdate       # Email templates
```

---

## 🤝 Contributing

This is a proprietary project for the Nigerian Academy of Audiology. 

For NAA members interested in contributing:
1. Contact the NAA Technology Committee
2. Request developer access
3. Follow the STYLE_GUIDE.md conventions
4. Submit pull requests for review

---

## 📞 Support & Contact

**Nigerian Academy of Audiology**

- 📧 Email: nigerianacademyofaudiology@gmail.com
- 🌐 Website: [naa-portal.onrender.com](https://naa-portal.onrender.com)
- 📍 Location: Lagos, Nigeria

**For Technical Issues:**
- Open an issue on GitHub (if authorized)
- Email technical support
- Contact the NAA Technology Committee

---

## 📜 License & Ownership

**© 2026 Nigerian Academy of Audiology**  
**All Rights Reserved**

This software is proprietary and intended exclusively for official Nigerian Academy of Audiology operations. Unauthorized use, reproduction, or distribution is strictly prohibited.

The NAA Portal is protected under Nigerian intellectual property laws and international copyright agreements.

---

## 🙏 Acknowledgments

**Built with:**
- Django Web Framework
- Medicio Bootstrap Theme
- Cloudinary Cloud Storage
- SendGrid Email Service
- Render Cloud Platform

**Special Thanks:**
- NAA Executive Committee
- NAA Technology Committee
- Student Chapter Representatives
- All NAA Members for their support

---

## 📈 Future Roadmap

### Q1 2026
- [ ] Mobile app (React Native)
- [ ] Payment integration for membership dues
- [ ] Advanced analytics dashboard
- [ ] Automated email campaigns

### Q2 2026
- [ ] Member directory with search
- [ ] Event management system
- [ ] Webinar hosting integration
- [ ] Member-to-member messaging

### Q3 2026
- [ ] Research collaboration platform
- [ ] Job board for audiologists
- [ ] Continuing education courses
- [ ] Professional certification tracking

---

**Built with ❤️ for the Nigerian Academy of Audiology**

**Last Updated:** February 2, 2026
