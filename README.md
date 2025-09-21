# Alejandro Ines Photography Portfolio

#### Video Demo: <URL HERE>
#### Description:
This project is my CS50x Final Project: a full-stack photography portfolio and blog website built using **Flask, SQLite, HTML, CSS, and JavaScript**.
It allows me to showcase my photography, write blog entries, and interact with visitors via a contact form and subscriber system.

---

## Features

- **Homepage (Hero Slider + Sphere Animation)**
  Animated copper sphere with ripple effects, inspirational quotes that update dynamically, and a climate countdown clock.

- **Gallery**
  Visitors can browse photos organized by tags: *Nature, Portraits, Candids, Experimental*.
  - Filter photos by category (instant transitions).
  - View images in a lightbox modal with a carousel.
  - Lazy-loading for smoother image rendering.
  - Admins can upload/edit/delete photos with tags.

- **Blog (Shutter Speed Soapbox)**
  - Posts with titles, body text, and optional images.
  - Dedicated post detail view.
  - All blog text is styled white on dark backgrounds for readability.
  - Subtle hover animations on blog images.

- **Search**
  - Navbar search bar works globally across the site.
  - Users can search posts and gallery photos.
  - Results are displayed with excerpts and linked to their full views.

- **About**
  - Bio section in a copper-themed transparent box.
  - Permanently white-highlighted headings and styled text for cameras and tools.

- **Contact**
  - Contact form (Formspree integration) with fields for name, email, and message.
  - Decorative framed contact photo.
  - Navbar search bar customized for consistent alignment and styling.

- **Admin Panel**
  - Login-protected dashboard.
  - Create, update, and delete blog posts.
  - Upload photos to the gallery with tags.
  - View and export email subscribers (CSV).
  - View and manage user messages.

---

## Technical Details

- **Framework:** Flask (Python)
- **Database:** SQLite (with `posts`, `gallery`, `subscribers`, `messages` tables)
- **Frontend:** HTML, Bootstrap 4, custom CSS
- **Scripting:** Vanilla JavaScript (theme toggle, search handler, climate clock, random quotes, image animations)
- **Deployment Ready:** Configured with `requirements.txt`, `Procfile`, `.gitignore`, and environment variables for production.

---

## File Structure

- `app.py` → Main Flask app, routes, and DB handling
- `templates/` → Jinja2 HTML templates (`base.html`, `index.html`, `gallery.html`, `blog.html`, `about.html`, `contact.html`, etc.)
- `static/styles.css` → Custom site-wide styling
- `static/scripts.js` → JavaScript for theme toggle, search, animations, etc.
- `static/uploads/` → User-uploaded blog post images
- `static/gallery_uploads/` → User-uploaded gallery photos
- `database.db` → SQLite database with all content
- `README.md` → Documentation file

---

## Design Choices

- **SQLite** chosen for simplicity and integration with Flask/CS50.
- **Copper/Navy Color Scheme** to give the site a unique, artistic, and “photographic” vibe.
- **Lazy-loading + CSS transitions** to smooth page loads.
- **Separation of templates and static files** for clean organization.
- **Admin authentication** via session cookies (lightweight but functional for a personal portfolio).

---

## Future Improvements

- Pagination for gallery and blog pages.
- User authentication for posting comments.
- Cloud storage for uploaded photos (AWS S3 or similar).
- SEO and meta tags for discoverability.

---

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/YOURUSERNAME/YOURPROJECT.git
   cd YOURPROJECT

2. Create this virtual environment:
    '''bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

3. Run the app:
    '''bash
    flask run

4. Vist http://localhost:5000 in your browser.

Acknowledgements:

Built as a CS50x 2025 Final Project.

Bootstrap for styling and responsive grid.

Formspree for contact form integration.

AI assistance was used for scaffolding and debugging (permitted for the final project), but all final implementation and design decisions are my own.
