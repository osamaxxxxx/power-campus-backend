using System.ComponentModel.DataAnnotations;

namespace webBackendGP.Models
{
    public enum UserRole
    {
        Admin,
        Instructor,
        Student
    }

    public class User
    {
        public int Id { get; set; }

        [Required]
        [MaxLength(100)]
        public string Name { get; set; } = string.Empty;

        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;

        [Required]
        public string PasswordHash { get; set; } = string.Empty;

        public UserRole Role { get; set; }
        
        // Navigation properties
        public ICollection<Enrollment> Enrollments { get; set; } = new List<Enrollment>();
        public ICollection<Course> InstructedCourses { get; set; } = new List<Course>();
    }
}
