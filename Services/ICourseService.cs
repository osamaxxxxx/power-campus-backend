using webBackendGP.DTOs;
using webBackendGP.Models;

namespace webBackendGP.Services
{
    public interface ICourseService
    {
        Task<IEnumerable<CourseResponseDto>> GetAllCoursesAsync();
        Task<Course?> CreateCourseAsync(CreateCourseDto courseDto);
        Task<CourseResponseDto?> UpdateCourseAsync(int id, CreateCourseDto courseDto);
        Task<bool> DeleteCourseAsync(int id);
        Task<bool> EnrollStudentAsync(int studentId, int courseId);
    }
}
