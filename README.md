# Power Campus Backend

Course Management System - Backend API built with .NET 9.0 Web API

## Features

- **Authentication & Authorization** - JWT-based authentication with role-based access control
- **User Management** - Admin, Instructor, and Student roles
- **Course Management** - Create, update, and manage courses
- **Enrollment System** - Student course registration
- **Scheduling** - Class schedule management
- **Grades** - Grade submission and reporting
- **Attendance** - Attendance tracking system

## Tech Stack

- .NET 9.0 Web API
- Entity Framework Core
- SQL Server
- JWT Authentication
- Swagger/OpenAPI

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### User Management (Admin)
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Courses
- `GET /api/courses` - List all courses
- `GET /api/courses/available` - Available courses
- `POST /api/courses` - Create course
- `PUT /api/courses/{id}` - Update course
- `DELETE /api/courses/{id}` - Delete course

### Enrollment
- `GET /api/enrollments/students/{id}/courses` - Student's courses
- `POST /api/enrollments` - Enroll student
- `DELETE /api/enrollments/{id}` - Drop course

### Scheduling
- `GET /api/schedule/student/{id}` - Student schedule
- `GET /api/schedule/doctor/{id}` - Instructor schedule
- `POST /api/schedule` - Create schedule
- `PUT /api/schedule/{id}` - Update schedule
- `DELETE /api/schedule/{id}` - Delete schedule

### Grades
- `GET /api/grades/student/{id}` - Student grades
- `GET /api/grades/course/{id}` - Course grades
- `POST /api/grades` - Submit grades

### Attendance
- `GET /api/attendance/student/{id}` - Student attendance
- `GET /api/attendance/course/{id}` - Course attendance
- `POST /api/attendance` - Mark attendance

## Getting Started

### Prerequisites
- .NET 9.0 SDK
- SQL Server

### Installation

1. Clone the repository:
```bash
git clone https://github.com/osamaxxxxx/power-campus-backend.git
cd power-campus-backend
```

2. Update connection string in `appsettings.json`

3. Run migrations:
```bash
dotnet ef database update
```

4. Run the application:
```bash
dotnet run
```

5. Access Swagger UI at `https://localhost:7065`

## Configuration

Update `appsettings.json` with your database connection string and JWT settings.

## License

MIT License
