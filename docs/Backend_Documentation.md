# Power Campus Backend Documentation

The Power Campus backend is a RESTful Web API built with .NET 9.0 that serves as the core infrastructure for the entire Course Management and Biometric Attendance System.

## Architecture

The backend follows a layered architectural pattern (N-Tier) to ensure clean separation of concerns and maintainability.

### Core Layers
- **Controllers Layer (`/Controllers`)**: Exposes HTTP endpoints. Handles incoming requests and maps them to the appropriate services. Includes controllers like `UsersController`, `CoursesController`, `AttendanceController`, etc.
- **Service Layer (`/Services`)**: Contains the core business logic of the application. The controllers depend on services to execute operations, keeping the API layer thin.
- **Repository Layer (`/Repositories`)**: Provides data access logic. It abstracts Entity Framework Core context (`DbContext`) away from the services, allowing for easier testing and swapping of data sources.
- **Data Access Layer (`/Data`)**: Contains the `ApplicationDbContext` (Entity Framework Core context) and database migrations.
- **Models (`/Models`)**: Contains the Entity models that represent database tables (e.g., `User`, `Course`, `Enrollment`, `AttendanceRecord`).
- **DTOs (`/DTOs`)**: Data Transfer Objects used to pass data between the client and server without exposing internal database models.

## Technology Stack
- **Framework**: ASP.NET Core Web API (.NET 9.0)
- **ORM**: Entity Framework Core 9.0
- **Database**: SQL Server
- **Authentication**: JWT (JSON Web Tokens)
- **Documentation**: Swagger/OpenAPI

## Security & Authentication
The system uses JWT-based authentication. 
- A user logs in via the `/api/auth/login` endpoint and receives a JWT token.
- This token must be included in the `Authorization` header (`Bearer <token>`) for protected routes.
- **Role-Based Access Control (RBAC)** is implemented. The system supports three roles:
  - `Admin`: Full access to user management, course creation, and system configuration.
  - `Instructor`: Can view assigned courses, manage grades, view attendance, and update their schedule.
  - `Student`: Can browse available courses, enroll/drop courses, view their own grades, schedule, and attendance records.

## Database Schema Highlights
- **Users**: Table for authentication and role management.
- **Courses**: Stores course metadata (Name, Credits, Description).
- **Enrollments**: A junction table linking Students to Courses.
- **Schedule**: Maps Courses to Instructors, Timeslots, and Rooms.
- **Grades**: Links Students, Courses, and numeric/letter grades.
- **Attendance**: Records daily biometric attendance for Students in specific Courses.

## API Endpoints (Summary)
Detailed interactive documentation is available via Swagger when running the project locally (`https://localhost:<port>/swagger`).

- `Auth`: Login and Registration endpoints.
- `Users`: CRUD operations for Admin user management.
- `Courses`: Browse, Create, Update, Delete courses.
- `Enrollments`: Student course registration.
- `Schedule`: Timetable management for students and instructors.
- `Grades`: Submit and view student grades.
- `Attendance`: Endpoints for the RPi face recognition system to submit logs, and for users to view attendance history.

## Setup & Execution

### Prerequisites
- .NET 9.0 SDK
- SQL Server LocalDB or a dedicated SQL Server instance.

### Configuration
Update the `appsettings.json` file in the root backend directory:
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=(localdb)\\mssqllocaldb;Database=PowerCampusDb;Trusted_Connection=True;MultipleActiveResultSets=true"
  },
  "Jwt": {
    "Key": "your_very_long_secret_key_here",
    "Issuer": "PowerCampusApi",
    "Audience": "PowerCampusUsers"
  }
}
```

### Running the Project
1. Open a terminal in the backend root directory.
2. Apply database migrations to create the schema:
   ```bash
   dotnet ef database update
   ```
3. Run the API:
   ```bash
   dotnet run
   ```
4. Open a browser and navigate to the local URL provided in the console (e.g., `https://localhost:7065/swagger`) to test the API endpoints.
