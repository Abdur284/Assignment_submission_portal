# Assignment Submission Portal

A simple Flask application for the DevOps Lab Mid assignment.

## Requirements
- Python 3.10 or newer
- pip

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation, run this for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the application

```powershell
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The SQLite database (`submissions.db`) is created automatically when the application starts. Valid submissions remain saved between application restarts.

## Features
- Student name, registration number, assignment title, and submission URL fields.
- Required-field validation on the server.
- HTTP/HTTPS URL validation on the server.
- Saves valid submissions to SQLite.
- Displays saved submissions in a table.
- Does not require file uploads.
