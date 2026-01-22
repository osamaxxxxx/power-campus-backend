using Microsoft.EntityFrameworkCore;
using webBackendGP.Data;
using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class EnrollmentService : IEnrollmentService
    {
        private readonly IRepository<Enrollment> _enrollmentRepository;
        private readonly AppDbContext _context;

        public EnrollmentService(IRepository<Enrollment> enrollmentRepository, AppDbContext context)
        {
            _enrollmentRepository = enrollmentRepository;
            _context = context;
        }

        public async Task<IEnumerable<EnrollmentResponseDto>> GetStudentCoursesAsync(int studentId)
        {
            var enrollments = await _context.Enrollments
                .Include(e => e.Student)
                .Include(e => e.Course)
                .Where(e => e.StudentId == studentId)
                .ToListAsync();

            return enrollments.Select(e => new EnrollmentResponseDto
            {
                Id = e.Id,
                StudentId = e.StudentId,
                StudentName = e.Student?.Name ?? "",
                CourseId = e.CourseId,
                CourseName = e.Course?.Title ?? "",
                EnrollmentDate = e.EnrollmentDate
            });
        }

        public async Task<EnrollmentResponseDto?> EnrollStudentAsync(EnrollmentDto enrollmentDto)
        {
            // Check if already enrolled
            var existing = await _enrollmentRepository.FindAsync(e => 
                e.StudentId == enrollmentDto.StudentId && e.CourseId == enrollmentDto.CourseId);
            
            if (existing.Any()) return null;

            var enrollment = new Enrollment
            {
                StudentId = enrollmentDto.StudentId,
                CourseId = enrollmentDto.CourseId,
                EnrollmentDate = DateTime.UtcNow
            };

            await _enrollmentRepository.AddAsync(enrollment);
            await _enrollmentRepository.SaveChangesAsync();

            // Reload with navigation properties
            var savedEnrollment = await _context.Enrollments
                .Include(e => e.Student)
                .Include(e => e.Course)
                .FirstOrDefaultAsync(e => e.Id == enrollment.Id);

            if (savedEnrollment == null) return null;

            return new EnrollmentResponseDto
            {
                Id = savedEnrollment.Id,
                StudentId = savedEnrollment.StudentId,
                StudentName = savedEnrollment.Student?.Name ?? "",
                CourseId = savedEnrollment.CourseId,
                CourseName = savedEnrollment.Course?.Title ?? "",
                EnrollmentDate = savedEnrollment.EnrollmentDate
            };
        }

        public async Task<bool> DropCourseAsync(int enrollmentId)
        {
            var enrollment = await _enrollmentRepository.GetByIdAsync(enrollmentId);
            if (enrollment == null) return false;

            _enrollmentRepository.Remove(enrollment);
            await _enrollmentRepository.SaveChangesAsync();
            return true;
        }
    }
}
