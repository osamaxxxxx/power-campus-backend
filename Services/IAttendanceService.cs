using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IAttendanceService
    {
        Task<IEnumerable<AttendanceResponseDto>> GetStudentAttendanceAsync(int studentId);
        Task<IEnumerable<AttendanceResponseDto>> GetCourseAttendanceAsync(int courseId);
        Task<AttendanceResponseDto?> MarkAttendanceAsync(AttendanceDto attendanceDto);
    }
}
