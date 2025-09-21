# Alejandro Ines — Photography Portfolio

#### Video Demo: <PASTE YOUTUBE URL>
### Live Deployment (via Render): https://aiphotographywebsiteblog.onrender.com/
#### GitHub Repo:https://github.com/YOURUSERNAME/YOURPROJECT.git

---

## Description

This project is my **CS50x Final Project**, a full-stack photography portfolio and blog web application. It is built with **Flask**, **SQLite**, **HTML/CSS (Bootstrap 4)**, and **JavaScript**.

The goal was to create a platform that looks like a personal online gallery: something that reflects both my photography style and my technical learning from CS50. I wanted it to feel modern and “artistic,” so I chose a **copper + navy blue color scheme**, subtle animations, and layout choices that emphasize photos.

The site has the following key sections: a **Homepage with a copper sphere ripple animation and quote box**, a **Gallery** with filters and a lightbox slider, a **Blog** with posts, an **About** page, a **Contact** form, a global **Search** feature, and an **Admin Panel** where I can manage content.

All blog posts, gallery images, subscribers, and messages are stored in a **SQLite database**. Uploaded photos are stored in `static/gallery_uploads/` and referenced from the database.

---

## Features

- **Homepage (Hero + Sphere Animation)**
  - Bootstrap carousel hero with photos.
  - A **copper 3D sphere** animation with ripple effects.
  - Dynamic “Food for Thought” quotes that update.
  - A copper divider line with shimmer effect.
  - Fully mobile-optimized (sphere shrinks and repositions on phones).

- **Gallery**
  - Visitors can browse photos organized into four tags: *Nature, Portraits, Candids, Experimental*.
  - **Filter controls** update the grid instantly with smooth fade transitions.
  - **Lightbox modal with carousel**: clicking any thumbnail opens a modal with next/previous controls, built directly from the thumbnails so the images always load.
  - Thumbnails have **lazy loading** and copper borders.
  - Admins can upload/edit/delete photos, and retag them if needed.

- **Blog (“Shutter Speed Soapbox”)**
  - Posts have title, kind (Journal, Note, Essay), body, and optional image.
  - List view shows posts chronologically.
  - Dedicated post detail page for each entry.
  - Text is styled for readability in dark mode.

- **Search**
  - Navbar search bar works across the site.
  - Can find both blog posts and gallery photos.
  - Results page shows excerpts and links to details.

- **About**
  - Bio section in a copper-framed box.
  - Notes about photography equipment.
  - Consistent theme styling.

- **Contact**
  - Contact form (via **Formspree**) with fields for name, email, and message.
  - Decorative framed contact photo.
  - Styled to match the rest of the site.

- **Admin Panel**
  - Login-protected (simple session-based auth).
  - Create, update, and delete blog posts.
  - Upload multiple photos at once to the gallery with a chosen tag.
  - Retag or delete photos after upload.
  - View and export subscribers to CSV.
  - View messages submitted via the contact form.

---

## Technical Details

- **Backend Framework:** Flask (Python)
- **Database:** SQLite, with 4 main tables (`posts`, `gallery`, `subscribers`, `messages`)
- **Frontend:** HTML (Jinja templates), Bootstrap 4, custom CSS
- **JavaScript:** Vanilla JS + jQuery for Bootstrap modal/carousel events
- **Deployment:** Configured with `requirements.txt`, `Procfile`, `.gitignore`, and environment variables. Deployed to **Render**.

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  kind TEXT NOT NULL DEFAULT 'Journal' CHECK (kind IN ('Journal','Note','Essay')),
  body TEXT NOT NULL,
  image_url TEXT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscribers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  message TEXT NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gallery (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  filename TEXT NOT NULL, -- relative path to file in static/gallery_uploads/
  tag TEXT NOT NULL CHECK (tag IN ('nature','portraits','candids','experimental')),
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

---

## File Structure
├── app.py                 # Main Flask application with routes, DB queries, admin auth
├── templates/             # Jinja2 templates
│   ├── base.html          # Layout shell (navbar, footer)
│   ├── index.html         # Homepage with hero + sphere animation
│   ├── gallery.html       # Gallery grid, filters, lightbox modal
│   ├── blog.html          # Blog index page
│   ├── post_detail.html   # Blog post detail page
│   ├── about.html         # About page
│   ├── contact.html       # Contact page
│   └── admin.html         # Admin dashboard
├── static/
│   ├── styles.css         # Custom CSS (copper theme, responsive tweaks, animations)
│   ├── scripts.js         # JavaScript (theme toggles, animations, filtering)
│   ├── gallery_uploads/   # Uploaded gallery photos
│   └── uploads/           # Uploaded blog post images
├── requirements.txt       # Python dependencies
├── Procfile               # Deployment entrypoint for Gunicorn
└── README.md              # Project documentation (this file)

---

## Design Choices
SQLite over MySQL/Postgres: lightweight and portable for a personal project.

Bootstrap grid system: ensures responsive design without writing custom grid CSS.

Copper/Navy theme: unique and visually striking for a photography portfolio.

Client-side filtering: fast, instant photo filtering without extra queries.

Lightbox built directly from gallery grid: avoids mismatches and missing photos.

Session-based admin auth: minimal but secure enough for single-user admin control.

---
How to Run Locally:
1. Clone the repo
git clone https://github.com/YOURUSERNAME/YOURPROJECT.git
cd YOURPROJECT

2. Create and activate virtual environment:
python3 -m venv venv
source venv/bin/activate      # macOS/Linux
# .\venv\Scripts\activate     # Windows

3. Install dependencies:
pip install -r requirements.txt

4. Run the app:
flask run

Then visit: http://localhost:5000

---

Deployment

This project is deployed on Render with GitHub auto-deploy enabled.

pip install -r requirements.txt

gunicorn app:app



---

## Future Improvements
Future Improvements

Add pagination for gallery and blog pages.

Implement user accounts and commenting.

Store uploads in cloud storage (e.g., S3, Cloudinary).

Improve SEO with meta tags and Open Graph data.

Enhance admin authentication with password hashing and role support.

---

## Acknowledgements
CS50 Staff & Community — for the course and guidance.

Bootstrap — for responsive front-end styling.

Formspree — for handling the contact form submissions.

Render — for deployment hosting.

AI Assistance — used for scaffolding and debugging (permitted by CS50), but all final code and design choices are my own.

My girlfriend Juliet - for being so supportive!
