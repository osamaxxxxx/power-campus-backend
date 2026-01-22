using Microsoft.EntityFrameworkCore;
using webBackendGP.Data;
using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class GradeService : IGradeService
    {
        private readonly IRepository<Grade> _gradeRepository;
        private readonly AppDbContext _context;

        public GradeService(IRepository<Grade> gradeRepository, AppDbContext context)
        {
            _gradeRepository = gradeRepository;
            _context = context;
        }

        public async Task<IEnumerable<GradeResponseDto>> GetStudentGradesAsync(int studentId)
        {
            var grades = await _context.Grades
                .Include(g => g.Student)
                .Include(g => g.Course)
                .Where(g => g.StudentId == studentId)
                .ToListAsync();

            return grades.Select(g => new GradeResponseDto
            {
                Id = g.Id,
                StudentId = g.StudentId,
                StudentName = g.Student?.Name ?? "",
                CourseId = g.CourseId,
                CourseName = g.Course?.Title ?? "",
                AssignmentName = g.AssignmentName,
                Score = g.Score,
                MaxScore = g.MaxScore,
                Percentage = g.MaxScore > 0 ? (g.Score / g.MaxScore) * 100 : 0
            });
        }

        public async Task<IEnumerable<GradeResponseDto>> GetCourseGradesAsync(int courseId)
        {
            var grades = await _context.Grades
                .Include(g => g.Student)
                .Include(g => g.Course)
                .Where(g => g.CourseId == courseId)
                .ToListAsync();

            return grades.Select(g => new GradeResponseDto
            {
                Id = g.Id,
                StudentId = g.StudentId,
                StudentName = g.Student?.Name ?? "",
                CourseId = g.CourseId,
                CourseName = g.Course?.Title ?? "",
                AssignmentName = g.AssignmentName,
                Score = g.Score,
                MaxScore = g.MaxScore,
                Percentage = g.MaxScore > 0 ? (g.Score / g.MaxScore) * 100 : 0
            });
        }

        public async Task<GradeResponseDto?> SubmitGradeAsync(CreateGradeDto gradeDto)
        {
            var grade = new Grade
            {
                StudentId = gradeDto.StudentId,
                CourseId = gradeDto.CourseId,
                AssignmentName = gradeDto.AssignmentName,
                Score = gradeDto.Score,
                MaxScore = gradeDto.MaxScore
            };

            await _gradeRepository.AddAsync(grade);
            await _gradeRepository.SaveChangesAsync();

            // Reload with navigation properties
            var savedGrade = await _context.Grades
                .Include(g => g.Student)
                .Include(g => g.Course)
                .FirstOrDefaultAsync(g => g.Id == grade.Id);

            if (savedGrade == null) return null;

            return new GradeResponseDto
            {
                Id = savedGrade.Id,
                StudentId = savedGrade.StudentId,
                StudentName = savedGrade.Student?.Name ?? "",
                CourseId = savedGrade.CourseId,
                CourseName = savedGrade.Course?.Title ?? "",
                AssignmentName = savedGrade.AssignmentName,
                Score = savedGrade.Score,
                MaxScore = savedGrade.MaxScore,
                Percentage = savedGrade.MaxScore > 0 ? (savedGrade.Score / savedGrade.MaxScore) * 100 : 0
            };
        }
    }
}
