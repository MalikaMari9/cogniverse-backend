# 🧠 Cogniverse Backend

A **FastAPI-based backend** for the AI Agent Simulation System.  
It handles authentication (JWT), user profiles, and PostgreSQL persistence — designed to scale with future modules like billing, simulations, and admin dashboards.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **Framework** | FastAPI |
| **Database** | PostgreSQL (via SQLAlchemy ORM) |
| **Auth** | JWT (Access + Refresh) |
| **Password Hashing** | bcrypt / Passlib |
| **File Uploads** | FastAPI `UploadFile` (local, ready for S3) |
| **Environment Config** | `pydantic-settings` |
| **Server** | Uvicorn |
| **Deployment Ready For** | AWS Lightsail / EC2 |

---

## 🗂️ Project Structure

backend/
│
├── app/
│ ├── main.py # FastAPI entrypoint
│ │
│ ├── core/
│ │ └── config.py # Environment variables and app settings
│ │
│ ├── db/
│ │ ├── database.py # DB engine and session setup
│ │ ├── models/
│ │ │ └── user_model.py # User ORM model
│ │ └── schemas/
│ │ └── user_schema.py # Pydantic schemas
│ │
│ ├── controllers/
│ │ ├── auth_controller.py # Register, login, logout logic
│ │ └── user_profile_controller.py # Profile CRUD logic
│ │
│ ├── routes/
│ │ ├── auth_routes.py # /auth endpoints
│ │ └── user_profile_routes.py # /users endpoints
│ │
│ └── services/
│ ├── jwt_service.py # Token creation, validation, revocation
│ ├── image_service.py # Profile image upload handler
│ └── utils/
│ └── auth_utils.py # Password hashing & verification helpers
│
├── requirements.txt # Python dependencies
└── .gitignore # Ignore envs, uploads, and caches

yaml
Copy code

---

## 🧩 Setup Guide

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/cogniverse-backend.git
cd cogniverse-backend/backend
2️⃣ Create and activate a virtual environment
bash
Copy code
python -m venv venv
venv\Scripts\activate     # on Windows
# source venv/bin/activate  # on Linux/Mac
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Create a .env file (in backend/)
bash
Copy code
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost/cogniverseDB
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
⚠️ Never commit .env to Git — it’s ignored by .gitignore.

5️⃣ Run the server (dev mode)
bash
Copy code
python -m uvicorn app.main:app --reload
Then open your browser at
👉 http://127.0.0.1:8000/docs
to explore your interactive Swagger API.

🧪 Test Endpoints (Postman or /docs)
Method	Endpoint	Description
POST	/auth/register	Create new user
POST	/auth/login	Login with username/email
GET	/auth/verify	Check JWT validity
POST	/auth/logout	Revoke active token
GET	/users/profile	Get user profile (JWT required)
PUT	/users/profile	Update username, email, or profile image

🧠 Example Requests
📝 Register
json
Copy code
POST /auth/register
{
  "username": "Marie",
  "email": "marie@example.com",
  "password": "Test12345"
}
🔑 Login
json
Copy code
POST /auth/login
{
  "identifier": "Marie",
  "password": "Test12345"
}
→ Returns:

json
Copy code
{
  "message": "Login successful",
  "access_token": "<JWT>",
  "refresh_token": "<JWT>"
}
Use the access_token for protected routes:

makefile
Copy code
Authorization: Bearer <access_token>
🧰 Development Notes
JWT tokens expire every 15 minutes (Access) and 7 days (Refresh).

Passwords are hashed with bcrypt before storage.

Profile images are saved to /uploads/profile_images/ (can be swapped with S3).

Role-based access and maintenance mode will be added soon.

🌐 Deployment Ready
Optimized for AWS Lightsail setup:

FastAPI via Uvicorn + Nginx

PostgreSQL on a separate instance

SSL via Certbot

Easily containerizable (Docker support planned)

👥 Contributors
Role	Name	Responsibility
💡 Founder / Backend Lead	You	Architecture, Auth, JWT, DB
🎨 UI & Frontend	Teammate A	React Frontend & UX
⚙️ Profile CRUD & API Integration	Teammate B	User module, testing

🧾 License
This project is private and for internal team development under the Cogniverse Project.
Do not distribute without permission.
