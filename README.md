# Assignment Review System - Backend

## Overview
The backend for the **Assignment Review System (ARS)** is built using **Django and Django REST Framework (DRF)**. It provides a robust API for managing users, assignments, and reviews. **Daphne** is used to handle WebSockets for real-time updates, and **PostgreSQL** serves as the database.

## Features
- **Authentication & Authorization**:
  - Traditional username-password authentication
  - Channel I OAuth and Google OAuth
  - Role-based access control (Admin, Reviewer, Reviewee)
- **Assignment Management**:
  - Create, edit, and allocate assignments.
  - Add sub-tasks and attach files (PDFs, DOCXs, images, links, etc.).
  - Multi-iteration review process with comments.
- **Review & Feedback**:
  - Multiple reviewers can assess assignments.
  - Real-time notifications via WebSockets.
- **Team Submissions**:
  - Enables group submissions for assignments.
- **User Profiles**:
  - Reviewers can view their review history and pending reviews.
  - Reviewees can track submission status and progress.
- **Real-Time Updates**:
  - Uses **Daphne** and **Django Channels** for WebSockets.
  - Live notifications and chat system.
- **Gamification & Reminders**:
  - Gamify the platform to encourage timely submissions.
  - Automated assignment reminders.

## Tech Stack
- **Django + Django REST Framework (DRF)**: Backend framework for APIs.
- **PostgreSQL**: Database for storing structured data.
- **Daphne + Django Channels**: WebSockets for real-time communication.
- **Celery + Redis**: Handles background tasks like notifications.

## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python (latest version)
- PostgreSQL
- Redis (for background tasks)
- Virtualenv (optional but recommended)

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ars-backend.git
   cd ars-backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `.env` file for database and secrets:
   ```env
   DATABASE_URL=postgres://youruser:yourpassword@localhost:5432/yourdb
   SECRET_KEY=your-secret-key
   REDIS_URL=redis://localhost:6379
   ```
5. Apply migrations:
   ```bash
   python manage.py migrate
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```
7. Start Daphne for WebSockets:
   ```bash
   daphne -b 0.0.0.0 -p 8001 ars.asgi:application
   ```

## Contributing
Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License
This project is licensed under the MIT License.

## Contact
For any inquiries or contributions, reach out at [aaryanjain888@gmail.com].

