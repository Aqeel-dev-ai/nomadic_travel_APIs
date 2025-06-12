# 🧭 Nomadic Travel - Django Backend

Nomadic Travel is a backend system for a modern travel and tourism platform built using **Django** and **Django REST Framework**. It enables tour listing, user authentication via JWT and Django-rest-registration, email verification, scheduling, and destination management.

---

## 🚀 Features

- 🔐 JWT-based user authentication (`SimpleJWT`)
- 📧 Email verification and password reset using `rest_registration`
- 🌍 Tour and destination management
- 📅 Scheduling support for tours
- 🛡️ Secure password validation and token blacklisting
- 📚 Interactive API documentation with Swagger (DRF-YASG)
- 📦 Media upload support (images, files)
- 🧪 Ready for Postman or frontend integration (React/Flutter/etc.)

---

## 📁 Project Structure

```

nomadic\_travel/
├── accounts/         # User-related logic (registration, login, etc.)
├── destination/      # Destination model and APIs
├── schedule/         # Schedule model and APIs
├── nomadic\_travel/   # Main Django config (settings, urls, wsgi)
├── media/            # Uploaded media files
├── db.sqlite3        # SQLite DB (dev)
└── manage.py

````

---

## 🔧 Tech Stack

- Python 3.10+
- Django 5.x
- Django REST Framework
- Simple JWT
- Rest Registration
- drf-yasg (Swagger API docs)
- SQLite (dev) / PostgreSQL (recommended for prod)

---

## ⚙️ Installation & Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/nomadic_travel.git
cd nomadic_travel
````

2. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file in the root directory**

```env
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password
```

5. **Apply migrations**

```bash
python manage.py migrate
```

6. **Create a superuser (admin)**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

Visit: [http://localhost:8000](http://localhost:8000)

---

## 🔑 Authentication & API Access

* The app uses **JWT** for authentication.
* Add `Authorization: Bearer <your_token>` header to secure endpoints.

---

## 📑 API Documentation (Swagger)

Visit: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
Provides interactive access to all APIs, including authentication, tours, destinations, and schedule.

---

## 🧪 Sample API Endpoints

| Method | Endpoint                 | Description            |
| ------ | ------------------------ | ---------------------- |
| POST   | `/api/account/register/` | Register new user      |
| POST   | `/api/account/login/`    | JWT login              |
| GET    | `/api/destinations/`     | List all destinations  |
| GET    | `/api/tours/`            | List all tours         |
| POST   | `/api/schedule/`         | Create a tour schedule |

> See Swagger docs for full list.

---

## 📦 Media & Static Files

* Media files are uploaded to `/media/` (configured via `MEDIA_ROOT`)
* Static files can be served using `STATIC_URL`

---

## 🛡️ Environment & Security Notes

* Don't use `DEBUG = True` in production.
* Always store secrets (like API keys or DB credentials) in `.env`.
* Use PostgreSQL or another production-grade DB for deployment.

---

## 📬 Contact

For issues, questions, or contributions:

* GitHub: [@Aqeel-dev-ai](https://github.com/Aqeel-dev-ai)
* Email: [aqeel032035@gmail.com](mailto:aqeel032035@gmail.com)


## 📜 License

This project is licensed under the **MIT License**.
