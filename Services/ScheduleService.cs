using Microsoft.EntityFrameworkCore;
using webBackendGP.Data;
using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class ScheduleService : IScheduleService
    {
        private readonly IRepository<Schedule> _scheduleRepository;
        private readonly AppDbContext _context;

        public ScheduleService(IRepository<Schedule> scheduleRepository, AppDbContext context)
        {
            _scheduleRepository = scheduleRepository;
            _context = context;
        }

        public async Task<IEnumerable<ScheduleResponseDto>> GetStudentScheduleAsync(int studentId)
        {
            // Get courses the student is enrolled in
            var enrolledCourseIds = await _context.Enrollments
                .Where(e => e.StudentId == studentId)
                .Select(e => e.CourseId)
                .ToListAsync();

            // Get schedules for those courses
            var schedules = await _context.Set<Schedule>()
                .Include(s => s.Course)
                .ThenInclude(c => c!.Instructor)
                .Where(s => enrolledCourseIds.Contains(s.CourseId))
                .ToListAsync();

            return schedules.Select(s => new ScheduleResponseDto
            {
                Id = s.Id,
                CourseId = s.CourseId,
                CourseName = s.Course?.Title ?? "",
                InstructorName = s.Course?.Instructor?.Name ?? "",
                DayOfWeek = s.DayOfWeek,
                StartTime = s.StartTime,
                EndTime = s.EndTime,
                Room = s.Room
            });
        }

        public async Task<IEnumerable<ScheduleResponseDto>> GetInstructorScheduleAsync(int instructorId)
        {
            var schedules = await _context.Set<Schedule>()
                .Include(s => s.Course)
                .ThenInclude(c => c!.Instructor)
                .Where(s => s.Course!.InstructorId == instructorId)
                .ToListAsync();

            return schedules.Select(s => new ScheduleResponseDto
            {
                Id = s.Id,
                CourseId = s.CourseId,
                CourseName = s.Course?.Title ?? "",
                InstructorName = s.Course?.Instructor?.Name ?? "",
                DayOfWeek = s.DayOfWeek,
                StartTime = s.StartTime,
                EndTime = s.EndTime,
                Room = s.Room
            });
        }

        public async Task<ScheduleResponseDto?> CreateScheduleAsync(ScheduleDto scheduleDto)
        {
            var schedule = new Schedule
            {
                CourseId = scheduleDto.CourseId,
                DayOfWeek = scheduleDto.DayOfWeek,
                StartTime = scheduleDto.StartTime,
                EndTime = scheduleDto.EndTime,
                Room = scheduleDto.Room
            };

            await _scheduleRepository.AddAsync(schedule);
            await _scheduleRepository.SaveChangesAsync();

            // Reload with navigation properties
            var savedSchedule = await _context.Set<Schedule>()
                .Include(s => s.Course)
                .ThenInclude(c => c!.Instructor)
                .FirstOrDefaultAsync(s => s.Id == schedule.Id);

            if (savedSchedule == null) return null;

            return new ScheduleResponseDto
            {
                Id = savedSchedule.Id,
                CourseId = savedSchedule.CourseId,
                CourseName = savedSchedule.Course?.Title ?? "",
                InstructorName = savedSchedule.Course?.Instructor?.Name ?? "",
                DayOfWeek = savedSchedule.DayOfWeek,
                StartTime = savedSchedule.StartTime,
                EndTime = savedSchedule.EndTime,
                Room = savedSchedule.Room
            };
        }

        public async Task<ScheduleResponseDto?> UpdateScheduleAsync(int id, ScheduleDto scheduleDto)
        {
            var schedule = await _scheduleRepository.GetByIdAsync(id);
            if (schedule == null) return null;

            schedule.CourseId = scheduleDto.CourseId;
            schedule.DayOfWeek = scheduleDto.DayOfWeek;
            schedule.StartTime = scheduleDto.StartTime;
            schedule.EndTime = scheduleDto.EndTime;
            schedule.Room = scheduleDto.Room;

            _scheduleRepository.Update(schedule);
            await _scheduleRepository.SaveChangesAsync();

            // Reload with navigation properties
            var updatedSchedule = await _context.Set<Schedule>()
                .Include(s => s.Course)
                .ThenInclude(c => c!.Instructor)
                .FirstOrDefaultAsync(s => s.Id == schedule.Id);

            if (updatedSchedule == null) return null;

            return new ScheduleResponseDto
            {
                Id = updatedSchedule.Id,
                CourseId = updatedSchedule.CourseId,
                CourseName = updatedSchedule.Course?.Title ?? "",
                InstructorName = updatedSchedule.Course?.Instructor?.Name ?? "",
                DayOfWeek = updatedSchedule.DayOfWeek,
                StartTime = updatedSchedule.StartTime,
                EndTime = updatedSchedule.EndTime,
                Room = updatedSchedule.Room
            };
        }

        public async Task<bool> DeleteScheduleAsync(int id)
        {
            var schedule = await _scheduleRepository.GetByIdAsync(id);
            if (schedule == null) return false;

            _scheduleRepository.Remove(schedule);
            await _scheduleRepository.SaveChangesAsync();
            return true;
        }
    }
}
