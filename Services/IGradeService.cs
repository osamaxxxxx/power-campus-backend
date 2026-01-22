using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IGradeService
    {
        Task<IEnumerable<GradeResponseDto>> GetStudentGradesAsync(int studentId);
        Task<IEnumerable<GradeResponseDto>> GetCourseGradesAsync(int courseId);
        Task<GradeResponseDto?> SubmitGradeAsync(CreateGradeDto gradeDto);
    }
}
