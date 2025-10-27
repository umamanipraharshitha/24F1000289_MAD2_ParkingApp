# Parking Lot Management System

A **web-based Parking Lot Management System** built using **Flask** that enables users to register, book, and release parking spots, while **admins** can manage lots, spots, and users via REST APIs.
The system supports background tasks, caching, and dynamic dashboards for both user and admin roles.


## Tech Stack

**Backend:**

* Flask — API backend and web framework
* Flask_SQLAlchemy — ORM for database management
* Flask-Mail — Outbound email notifications
* Celery — Background job queue for emails and exports
* Redis — Message broker and caching system
* Flask-CORS — Cross-origin support for frontend communication
* Werkzeug.security — Password hashing and security
* SQLite — Lightweight development database

**Frontend:**

* Bootstrap — Responsive UI and layout
* Vue.js — Reactive, component-based front-end

---

## ⚙️ Why These Technologies

* **Celery + Redis** → Handle background jobs like emails and CSV exports without blocking user actions.
* **Bootstrap** → Ensures a clean, mobile-friendly, and consistent interface.
* **Vue.js** → Adds real-time interactivity and smooth, SPA-like user experience.

---

##  Database Schema

**User**
`id`, `username`, `email`, `password_hash`, `role`, `created_at`

**ParkingLot**
`id`, `prime_location_name`, `price`, `address`, `pin_code`, `number_of_spots`, `created_at`

**ParkingSpot**
`id`, `lot_id (FK)`, `status ('A' for available, 'O' for occupied)`, `created_at`

**Reservation**
`id`, `spot_id (FK)`, `user_id (FK)`, `parking_timestamp`, `leaving_timestamp`, `status`, `parking_cost`

---

## 🔌 API Endpoints

### **Authentication**

* `/api/register`
* `/api/login`
* `/api/logout`

### **User APIs**

* `/api/user/dashboard`
* `/api/book_spot/<lot_id>`
* `/api/release_spot/<reservation_id>`
* `/api/profile`
* `/api/edit_profile`

### **Admin APIs**

* `/api/admin/dashboard`
* `/api/create_lot`
* `/api/admin/users`
* `/api/admin/lot/<lot_id>/spots`

### **Lot & Spot Management**

* `/api/lot/<lot_id>/edit`
* `/api/lot/<lot_id>/delete`
* `/api/admin/spot/<spot_id>/edit`
* `/api/admin/spot/<spot_id>/delete`

### **Reporting & Export**

* `/api/search`
* `/api/export-csv`
* `/api/admin/summary`
* `/api/user/summary`

> All endpoints use **JSON** for communication and are protected by **role-based decorators**.

---

##  Architecture

**Backend:**

* `app.py` → Main Flask application, routes, logic, and decorators.
* `models/` → SQLAlchemy ORM models for all entities.
* `cache.py` → Redis-based caching utilities.
* `tasks.py` → Celery workers for async operations.

**Frontend:**

* Built with **Bootstrap** and **Vue.js**, providing real-time interactivity and seamless API integration.

---

## Implemented Features

* User registration, login, and dashboard management.
* Admin dashboard for lot, spot, and user management.
* Role-based access and session security.
* Responsive, mobile-friendly design.
* Background jobs for emails and CSV exports.
* Redis caching for fast, optimized data retrieval.
* Secure password handling and protection.
* Automated email notifications (spot booking, inactivity).
* CSV export for reservation history.
* Real-time notifications when a spot is booked.
* User password change option for better security.

---

