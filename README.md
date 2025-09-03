# Athlete Performance Tracker

<p align="center"> 
 <img src="https://github.com/user-attachments/assets/b2e309ad-9fdc-43cf-81e8-37b4a46e9d85" width="800" />
</p>

A full-stack web application for managing, visualizing, and analyzing cyclist performance data. Built with FastAPI (backend), Streamlit (frontend), and SQLite (database).

---

## Features

- **User Authentication:** Secure login for athletes and admins.
- **Role-Based Access:** Admins manage users, athletes, and performance data; athletes view and analyze their own data.
- **User Management:** Register, edit, and delete users; assign roles.
- **Athlete Management:** Add, edit, and delete athlete profiles.
- **Performance Data:** Ingest, view, and analyze performance metrics (Power, VO2 Max, Heart Rate, etc.).
- **Dashboards:**  
  - Athlete Dashboard: Personal performance trends and comparisons.
  - Admin Dashboard: Top performers, aggregated trends, and athlete comparisons.
- **Data Visualization:** Interactive charts (Plotly) for trends, comparisons, and correlations.
- **API Endpoints:** RESTful endpoints for all core resources.
- **CSV Data Ingestion:** Scripts and services for importing bulk data.

---

## Project Structure

```
sql-fastapi/
│
├── backend/                # FastAPI backend
│   ├── main.py             # App entrypoint
│   ├── config.py           # App settings (uses .env for secrets)
│   ├── database.py         # SQLite DB setup
│   ├── models/             # Pydantic models
│   ├── routers/            # API endpoints (user, athlete, performance, auth)
│   ├── services/           # Data ingestion, utilities
│   ├── utils/              # Security, CSV processing
│
├── streamlit/              # Streamlit frontend
│   ├── app.py              # Main UI entrypoint
│   ├── pages/              # Dashboard, management, profile, history
│   ├── utils/              # API and auth helpers
│
├── data/                   # Raw CSV data files
├── scripts/                # Utility scripts (admin, faker, migration)
├── requirements.txt        # Python dependencies
├── cyclist_database.db     # SQLite database file
├── .env                    # Environment variables (not tracked in git)
└── README.md               # Project documentation
```

---

## Setup & Installation

1. **Clone the repository:**
	```bash
	git clone https://github.com/<your-username>/sql-fastapi.git
	cd sql-fastapi
	```

2. **Create and activate a virtual environment:**
	```bash
	python -m venv .venv
	source .venv/bin/activate
	```

3. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```

4. **Configure environment variables:**
	- Copy `.env.example` to `.env` and set your secrets (e.g., `SECRET_KEY`, `DATABASE_URL`).
	- **Never commit your `.env` file to git.**

5. **Initialize the database:**
	- The database is auto-initialized on backend startup.

---

## Running the App

**Start the FastAPI backend:**
```bash
PYTHONPATH=. python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

**Start the Streamlit frontend:**
```bash
streamlit run streamlit/app.py
```

- Access the UI at [http://localhost:8501](http://localhost:8501)
- The backend API runs at [http://127.0.0.1:8001](http://127.0.0.1:8001)

---

## Usage

- **Admins:**  
  - Manage users and athletes.
  - View top performers and compare athletes.
  - Ingest and manage performance data.

- **Athletes:**  
  - View personal dashboard and performance history.
  - Compare own metrics to top performers.

---

## Testing & Development

- Unit tests can be added in the `tests/` directory.
- Use scripts in `scripts/` for admin tasks, data population, and migrations.

---

## Security Notes

- Secrets and sensitive config should be stored in `.env` (never in code or git).
- Passwords are hashed using bcrypt or pbkdf2_sha256.

---

## Contributing

Pull requests and issues are welcome!  
Please follow best practices for Python, FastAPI, and Streamlit.

---

## License

MIT License

---

## Author

Michael Adebayo ([@MichAdebayo](https://github.com/MichAdebayo))


