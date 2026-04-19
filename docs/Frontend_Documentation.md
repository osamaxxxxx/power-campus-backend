# Power Campus Frontend Documentation

The Power Campus frontend is a modern, responsive Single Page Application (SPA) built with React and Vite. It serves as the main interactive portal for Students, Instructors, and Administrators.

## Architecture & Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite (for fast, optimized builds and hot-module replacement)
- **Routing**: React Router DOM v6
- **HTTP Client**: Axios (configured with interceptors for JWT token attachment)
- **Icons**: Lucide React
- **Styling**: Vanilla CSS with full Dark Mode support and responsive design principles.

## Directory Structure
The main source code is located in `frontend/src`:

- `/api`: Contains Axios configuration and centralized API service functions.
- `/assets`: Static assets like images (e.g., `logo-english.png`).
- `/components`: Reusable UI components (e.g., Sidebar, Navbar, Modal, Buttons).
- `/contexts`: React Context providers for global state management (e.g., `AuthContext`, `ThemeContext`).
- `/pages`: Top-level page components representing different routes in the application.

## Key Features by Role

The UI dynamically adapts based on the logged-in user's role (Admin, Instructor, Student), authenticated via JWT claims.

### Admin
- **User Management**: View, add, edit, and delete users across the system.
- **System Overview**: Full access to all scheduling and course creation tools.

### Instructor
- **My Courses**: View courses they are assigned to teach.
- **Grades Management**: Select a course, view enrolled students, and input/update grades.
- **Schedule**: View their personal teaching schedule (read-only or manageable depending on configuration).

### Student
- **Course Catalog**: Browse available courses and enroll.
- **My Courses**: View enrolled courses with an option to drop them.
- **My Schedule**: View a personalized weekly timetable.
- **My Grades**: View their grades for completed courses.
- **My Attendance**: Track attendance records logged by the biometric system.

## UI / UX Design
- **Responsive Layout**: The application uses a Sidebar + Main Content layout. The sidebar is collapsible on smaller screens (mobile-friendly).
- **Dark Mode**: Integrated via a toggle switch. The CSS relies heavily on CSS Variables (`--bg-primary`, `--text-primary`, etc.) to switch color palettes seamlessly.
- **Animations**: Micro-interactions on buttons, smooth page transitions, and modern glassmorphism UI elements to provide a premium feel.

## State Management & Authentication
- **AuthContext**: Manages the user's login state. Upon login, the JWT token is stored in `localStorage`. `AuthContext` parses the token to extract user details (ID, Name, Role) and makes them available globally.
- **Protected Routes**: React Router is configured with wrapper components that check if a user is authenticated (and authorized for specific roles) before rendering protected pages. If unauthenticated, users are redirected to `/login`.

## Setup & Execution

### Prerequisites
- Node.js (v18+)
- npm or yarn

### Installation
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the necessary Node modules:
   ```bash
   npm install
   ```

### Configuration
Update the backend API URL if needed. This is typically configured in `.env` or inside `src/api/axiosConfig.js` (pointing to `https://localhost:7065/api` by default).

### Running the App
Start the Vite development server:
```bash
npm run dev
```
The application will usually be available at `http://localhost:5173`.
