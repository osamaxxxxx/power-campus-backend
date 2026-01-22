using Microsoft.EntityFrameworkCore;
using webBackendGP.Data;
using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class AttendanceService : IAttendanceService
    {
        private readonly IRepository<Attendance> _attendanceRepository;
        private readonly AppDbContext _context;

        public AttendanceService(IRepository<Attendance> attendanceRepository, AppDbContext context)
        {
            _attendanceRepository = attendanceRepository;
            _context = context;
        }

        public async Task<IEnumerable<AttendanceResponseDto>> GetStudentAttendanceAsync(int studentId)
        {
            var attendances = await _context.Attendances
                .Include(a => a.Student)
                .Include(a => a.Course)
                .Where(a => a.StudentId == studentId)
                .OrderByDescending(a => a.Date)
                .ToListAsync();

            return attendances.Select(a => new AttendanceResponseDto
            {
                Id = a.Id,
                StudentId = a.StudentId,
                StudentName = a.Student?.Name ?? "",
                CourseId = a.CourseId,
                CourseName = a.Course?.Title ?? "",
                Date = a.Date,
                IsPresent = a.IsPresent
            });
        }

        public async Task<IEnumerable<AttendanceResponseDto>> GetCourseAttendanceAsync(int courseId)
        {
            var attendances = await _context.Attendances
                .Include(a => a.Student)
                .Include(a => a.Course)
                .Where(a => a.CourseId == courseId)
                .OrderByDescending(a => a.Date)
                .ThenBy(a => a.Student!.Name)
                .ToListAsync();

            return attendances.Select(a => new AttendanceResponseDto
            {
                Id = a.Id,
                StudentId = a.StudentId,
                StudentName = a.Student?.Name ?? "",
                CourseId = a.CourseId,
                CourseName = a.Course?.Title ?? "",
                Date = a.Date,
                IsPresent = a.IsPresent
            });
        }

        public async Task<AttendanceResponseDto?> MarkAttendanceAsync(AttendanceDto attendanceDto)
        {
            // Check if attendance already exists for this student, course, and date
            var existingAttendance = await _context.Attendances
                .FirstOrDefaultAsync(a => 
                    a.StudentId == attendanceDto.StudentId && 
                    a.CourseId == attendanceDto.CourseId && 
                    a.Date.Date == attendanceDto.Date.Date);

            if (existingAttendance != null)
            {
                // Update existing attendance
                existingAttendance.IsPresent = attendanceDto.IsPresent;
                _attendanceRepository.Update(existingAttendance);
                await _attendanceRepository.SaveChangesAsync();

                var updated = await _context.Attendances
                    .Include(a => a.Student)
                    .Include(a => a.Course)
                    .FirstOrDefaultAsync(a => a.Id == existingAttendance.Id);

                if (updated == null) return null;

                return new AttendanceResponseDto
                {
                    Id = updated.Id,
                    StudentId = updated.StudentId,
                    StudentName = updated.Student?.Name ?? "",
                    CourseId = updated.CourseId,
                    CourseName = updated.Course?.Title ?? "",
                    Date = updated.Date,
                    IsPresent = updated.IsPresent
                };
            }

            // Create new attendance record
            var attendance = new Attendance
            {
                StudentId = attendanceDto.StudentId,
                CourseId = attendanceDto.CourseId,
                Date = attendanceDto.Date,
                IsPresent = attendanceDto.IsPresent
            };

            await _attendanceRepository.AddAsync(attendance);
            await _attendanceRepository.SaveChangesAsync();

            // Reload with navigation properties
            var savedAttendance = await _context.Attendances
                .Include(a => a.Student)
                .Include(a => a.Course)
                .FirstOrDefaultAsync(a => a.Id == attendance.Id);

            if (savedAttendance == null) return null;

            return new AttendanceResponseDto
            {
                Id = savedAttendance.Id,
                StudentId = savedAttendance.StudentId,
                StudentName = savedAttendance.Student?.Name ?? "",
                CourseId = savedAttendance.CourseId,
                CourseName = savedAttendance.Course?.Title ?? "",
                Date = savedAttendance.Date,
                IsPresent = savedAttendance.IsPresent
            };
        }
    }
}
