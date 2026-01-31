using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IEnrollmentService
    {
        Task<IEnumerable<EnrollmentResponseDto>> GetStudentCoursesAsync(int studentId);
        Task<IEnumerable<EnrollmentResponseDto>> GetCourseEnrollmentsAsync(int courseId);
        Task<EnrollmentResponseDto?> EnrollStudentAsync(EnrollmentDto enrollmentDto);
        Task<bool> DropCourseAsync(int enrollmentId);
    }
}
