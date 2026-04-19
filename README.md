# Power Campus

Power Campus is a comprehensive Course Management and Attendance System. It consists of three main components: a .NET 9.0 Backend API, a React/Vite Frontend, and a Raspberry Pi-based Face Recognition Attendance System.

## Project Structure

- **Backend**: .NET 9.0 Web API providing core business logic, user management, and data persistence.
- **Frontend**: React application (built with Vite) serving as the main user interface for students, instructors, and administrators.
- **RPiFaceAttendance**: Python application for Raspberry Pi using YOLOv8 and DeepFace for biometric student attendance tracking.

---

## 1. Backend (.NET 9.0 Web API)

The backend provides a robust API for managing users, courses, enrollments, schedules, grades, and attendance.

### Features
- **Authentication & Authorization** - JWT-based authentication with role-based access control
- **User Management** - Admin, Instructor, and Student roles
- **Course Management** - Create, update, and manage courses
- **Enrollment System** - Student course registration
- **Scheduling** - Class schedule management
- **Grades** - Grade submission and reporting
- **Attendance** - Attendance tracking system

### Tech Stack
- .NET 9.0 Web API
- Entity Framework Core
- SQL Server
- JWT Authentication
- Swagger/OpenAPI

### Getting Started (Backend)
1. Navigate to the backend root directory.
2. Update the connection string in `appsettings.json`.
3. Run migrations:
   ```bash
   dotnet ef database update
   ```
4. Run the application:
   ```bash
   dotnet run
   ```
5. Access Swagger UI at `https://localhost:7065` (or the configured port).

---

## 2. Frontend (React + Vite)

The frontend provides an intuitive UI for the Power Campus system, including responsive design and dark mode support.

### Tech Stack
- React 18
- Vite
- React Router DOM
- Axios
- Lucide React (Icons)
- CSS (Custom styling with Dark Mode)

### Getting Started (Frontend)
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

---

## 3. RPi Face Attendance System (Python)

A standalone application designed to run on a Raspberry Pi (or PC) to capture student faces and automatically record attendance.

### Tech Stack
- Python 3.x
- YOLOv8 (Face detection)
- DeepFace (Face recognition)
- Tkinter (GUI)
- Requests (API communication)

### Getting Started (RPi Face Attendance)
1. Navigate to the `RPiFaceAttendance` directory:
   ```bash
   cd RPiFaceAttendance
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python src/main.py
   ```

---

## License

MIT License
