using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IScheduleService
    {
        Task<IEnumerable<ScheduleResponseDto>> GetStudentScheduleAsync(int studentId);
        Task<IEnumerable<ScheduleResponseDto>> GetInstructorScheduleAsync(int instructorId);
        Task<ScheduleResponseDto?> CreateScheduleAsync(ScheduleDto scheduleDto);
        Task<ScheduleResponseDto?> UpdateScheduleAsync(int id, ScheduleDto scheduleDto);
        Task<bool> DeleteScheduleAsync(int id);
    }
}
