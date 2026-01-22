using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IEnrollmentService
    {
        Task<IEnumerable<EnrollmentResponseDto>> GetStudentCoursesAsync(int studentId);
        Task<EnrollmentResponseDto?> EnrollStudentAsync(EnrollmentDto enrollmentDto);
        Task<bool> DropCourseAsync(int enrollmentId);
    }
}
