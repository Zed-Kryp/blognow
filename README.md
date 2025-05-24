# BlogNow - Simple Blogging Website

A simple blogging website built with Python Flask backend and vanilla HTML/CSS frontend.

## Features

- Blog feed with filtering and sorting
- Individual blog view with comments and likes
- Blog editor for authors
- User profiles
- Role-based access control
- Local SQLite database

## Project Structure

```
blognow-local/
├── static/
│   ├── css/
│   │   ├── common.css
│   │   ├── home.css
│   │   ├── blog.css
│   │   ├── editor.css
│   │   └── profile.css
│   └── js/
│       ├── common.js
│       ├── home.js
│       ├── blog.js
│       ├── editor.js
│       └── profile.js
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── blog.html
│   ├── editor.html
│   └── profile.html
├── app.py
├── models.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```bash
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Development

- The application uses SQLite as the database
- No authentication is implemented yet - using mock users
- All styling is done with custom CSS (no frameworks)
- Frontend uses vanilla JavaScript for interactivity 