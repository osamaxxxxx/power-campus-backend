using System.ComponentModel.DataAnnotations;
using webBackendGP.Models;

namespace webBackendGP.DTOs
{
    public class LoginDto
    {
        [Required]
        public string Email { get; set; } = string.Empty;
        [Required]
        public string Password { get; set; } = string.Empty;
    }

    public class RegisterDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;
        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;
        [Required]
        public string Password { get; set; } = string.Empty;
        public UserRole Role { get; set; } = UserRole.Student;
    }

    public class AuthResponseDto
    {
        public int Id { get; set; }
        public string Token { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
    }

    public class CreateCourseDto
    {
        [Required]
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int CreditHours { get; set; }
        public int? InstructorId { get; set; }
    }
    
    public class CourseResponseDto
    {
        public int Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public int CreditHours { get; set; }
        public string InstructorName { get; set; } = string.Empty;
    }

    public class CreateGradeDto
    {
        public int StudentId { get; set; }
        public int CourseId { get; set; }
        public string AssignmentName { get; set; } = string.Empty;
        public double Score { get; set; }
        public double MaxScore { get; set; }
    }

    public class GradeResponseDto
    {
        public int Id { get; set; }
        public int StudentId { get; set; }
        public string StudentName { get; set; } = string.Empty;
        public int CourseId { get; set; }
        public string CourseName { get; set; } = string.Empty;
        public string AssignmentName { get; set; } = string.Empty;
        public double Score { get; set; }
        public double MaxScore { get; set; }
        public double Percentage { get; set; }
    }

    // User Management DTOs
    public class UserResponseDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
    }

    public class UpdateUserDto
    {
        public string? Name { get; set; }
        public string? Email { get; set; }
        public string? Password { get; set; }
        public UserRole? Role { get; set; }
    }

    // Enrollment DTOs
    public class EnrollmentDto
    {
        public int StudentId { get; set; }
        public int CourseId { get; set; }
    }

    public class EnrollmentResponseDto
    {
        public int Id { get; set; }
        public int StudentId { get; set; }
        public string StudentName { get; set; } = string.Empty;
        public int CourseId { get; set; }
        public string CourseName { get; set; } = string.Empty;
        public DateTime EnrollmentDate { get; set; }
    }

    // Schedule DTOs
    public class ScheduleDto
    {
        public int CourseId { get; set; }
        public DayOfWeek DayOfWeek { get; set; }
        public TimeSpan StartTime { get; set; }
        public TimeSpan EndTime { get; set; }
        public string Room { get; set; } = string.Empty;
    }

    public class ScheduleResponseDto
    {
        public int Id { get; set; }
        public int CourseId { get; set; }
        public string CourseName { get; set; } = string.Empty;
        public string InstructorName { get; set; } = string.Empty;
        public DayOfWeek DayOfWeek { get; set; }
        public TimeSpan StartTime { get; set; }
        public TimeSpan EndTime { get; set; }
        public string Room { get; set; } = string.Empty;
    }

    // Attendance DTOs
    public class AttendanceDto
    {
        public int StudentId { get; set; }
        public int CourseId { get; set; }
        public int? LectureId { get; set; }
        public DateTime Date { get; set; }
        public bool IsPresent { get; set; }
    }

    public class AttendanceResponseDto
    {
        public int Id { get; set; }
        public int StudentId { get; set; }
        public string StudentName { get; set; } = string.Empty;
        public int CourseId { get; set; }
        public string CourseName { get; set; } = string.Empty;
        public int? LectureId { get; set; }
        public string? LectureTitle { get; set; }
        public DateTime Date { get; set; }
        public bool IsPresent { get; set; }
    }

    // Lecture DTOs
    public class CreateLectureDto
    {
        [Required]
        public int CourseId { get; set; }
        [Required]
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        [Required]
        public DateTime Date { get; set; }
        public TimeSpan StartTime { get; set; }
        public TimeSpan EndTime { get; set; }
    }

    public class LectureResponseDto
    {
        public int Id { get; set; }
        public int CourseId { get; set; }
        public string CourseName { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public DateTime Date { get; set; }
        public TimeSpan StartTime { get; set; }
        public TimeSpan EndTime { get; set; }
    }
}
