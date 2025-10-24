🧠 CogniVerse Backend

FastAPI-based backend for the CogniVerse AI Simulation Platform — managing projects, agents, billing, access control, and system configurations.

⚙️ 1. Prerequisites

Before starting, make sure you have:

Python 3.10+

PostgreSQL 14+

Git

(Optional) Virtual environment manager such as venv or virtualenv

🏗️ 2. Clone and Setup Environment
git clone https://github.com/MalikaMari9/cogniverse-backend.git
cd cogniverse-backend/backend


Create and activate virtual environment:

Windows (PowerShell):

python -m venv venv
venv\Scripts\activate


Linux / macOS:

python3 -m venv venv
source venv/bin/activate

📦 3. Install Dependencies
pip install -r requirements.txt


If you add new packages, freeze them for version control:

pip freeze > requirements.txt

🧩 4. Environment Variables

Create a .env file in backend/ with your configuration:

DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/db
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

🗃️ 5. Database Setup

Create a PostgreSQL database:

CREATE DATABASE cogniverseDB;


Run migrations or create tables automatically:

python -m app.db.init_db


(Optional) Seed initial data:

python -m app.db.seeds.seed_access_control
python -m app.db.seeds.seed_config
python -m app.db.seeds.seed_maintenance

🚀 6. Run the Application

Development mode:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


Production mode:

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000


The API will be available at:
👉 http://127.0.0.1:8000

Interactive docs:
👉 http://127.0.0.1:8000/docs

🧠 7. Project Structure
cogniverse-backend/
└── backend/
    ├── app/
    │   ├── controllers/
    │   ├── db/
    │   │   ├── models/
    │   │   ├── schemas/
    │   │   ├── seeds/
    │   ├── routes/
    │   ├── services/
    │   ├── main.py
    │   └── __init__.py
    ├── requirements.txt
    └── README.md

🧰 8. Common Commands
Purpose	Command
Recreate DB tables	python -m app.db.init_db
Seed base configs	python -m app.db.seeds.seed_config
Start server	uvicorn app.main:app --reload
Lint	flake8 app
Format	black app
🔐 9. Notes

SuperAdmins bypass maintenance mode automatically.

Default roles and permissions are created by seed scripts.

JWT cookies (HTTP-only) are used for secure authentication.

Logging system tracks all major actions in system_log_tbl.
