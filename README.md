# 📦 Job Management Backend API

## 🧠 Project Overview

This project is a backend API designed for a small operations company that manages field teams responsible for scheduled jobs such as equipment servicing, site inspections, and deliveries.

Previously, operations were tracked using spreadsheets, which led to inefficiencies, lack of scalability, and poor auditability. This system replaces that workflow with a structured, scalable, and maintainable backend service that enables:

* Centralized staff management
* Efficient job scheduling and assignment
* Real-time job tracking
* Activity logging for accountability

---

## 🏗️ Architecture & Design Decisions

### 🔹 FastAPI

FastAPI was chosen for its:

* High performance (ASGI-based)
* Automatic Swagger/OpenAPI documentation
* Strong support for type validation using Pydantic

### 🔹 PostgreSQL

PostgreSQL was selected because:

* It provides strong relational integrity
* It is well-suited for structured data such as users, jobs, and logs
* It scales reliably for production systems

### 🔹 SQLAlchemy (ORM)

SQLAlchemy was used to:

* Abstract database interactions
* Enable clean model definitions
* Support complex queries (joins, filtering, search)

### 🔹 Modular Architecture

The project follows a clean modular structure:

* **Routers** → Handle HTTP requests/responses
* **Schemas** → Define request/response validation (Pydantic)
* **Services** → Contain business logic (separation of concerns)

This separation improves:

* Maintainability
* Testability
* Readability

---

## 🔐 Authentication & Authorization

### ✅ JWT Authentication

* Users authenticate via a login endpoint
* A JWT token is generated and returned
* Token is used to access protected routes

### ✅ Role-Based Access Control (RBAC)

The system supports three roles:

* **Admin/Manager** → Full access and  Operational control
* **Staff** → Limited to assigned jobs

---

## 🚀 Features Implemented

### 👥 Staff Management

* Create staff members
* Assign roles (admin, manager, staff)

### 🔑 Authentication

* Secure login using JWT
* Password hashing implemented

### 📋 Job Management

* Create jobs
* Assign jobs to staff
* Track job lifecycle (pending → assigned → in_progress → completed)

### 🔍 Search & Filtering

* Search across:

  * Job title
  * Job description
* Filter by:

  * Status
  * Start time
  * End time

### 📜 Activity Logging

* Tracks system actions for auditability

---

## ⚙️ Key Engineering Decisions

### 🔹 Services Layer (Separation of Concerns)

Business logic is isolated in the services layer instead of routers.
This ensures:

* Cleaner endpoints
* Reusable logic
* Easier debugging and scaling

---

### 🔹 Handling bcrypt 72-byte Limitation

bcrypt has a 72-byte password limit.
This was handled by pre-hashing passwords before applying bcrypt, preventing runtime errors and ensuring security.

---

### 🔹 Multi-Field Search Implementation

Search functionality was implemented across multiple fields using SQLAlchemy filters, enabling flexible querying of jobs and staff.

---

### 🔹 Pydantic v2 Compatibility

Used:

```python
from_attributes = True
```

This allows seamless conversion of SQLAlchemy models to response schemas.

---

## 📁 Project Structure

```bash
.
├── alembic/
├── app/
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── job.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── job.py
│   │   └── staff.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── job.py
│   │
│   ├── __init__.py
│   ├── models.py
│   ├── rquirements.txt
│   ├── database.py
│   ├── security.py
│   ├── logger.py
│   └── main.py
│
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── README.md
└── app.log
```

---

## 🐳 Running the Project

### 🔹 Using Docker

```bash
docker-compose up --build
```

---

### 🔹 Running Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

### 🔹 Access API Docs

Once running:

* Swagger UI: `http://localhost:8000/docs`

---

## 🧪 Testing

* API endpoints were tested using Swagger UI

---

## 🧑‍💻 Final Notes

This project emphasizes:

* Clean architecture
* Separation of concerns
* Practical backend design for real-world use cases

The goal was not just to build functionality, but to structure the system in a way that is maintainable, scalable, and ready for frontend integration.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📫 Contact

For any questions or support:

* Email: [ezesam227@gmail.com](mailto:ezesam227@gmail.com)
* GitHub: OnyekachiEzeala

