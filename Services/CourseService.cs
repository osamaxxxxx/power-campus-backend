using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class CourseService : ICourseService
    {
        private readonly IRepository<Course> _courseRepo;
        private readonly IRepository<Enrollment> _enrollmentRepo;
        private readonly IRepository<User> _userRepo;

        public CourseService(IRepository<Course> courseRepo, IRepository<Enrollment> enrollmentRepo, IRepository<User> userRepo)
        {
            _courseRepo = courseRepo;
            _enrollmentRepo = enrollmentRepo;
            _userRepo = userRepo;
        }

        public async Task<IEnumerable<CourseResponseDto>> GetAllCoursesAsync()
        {
            var courses = await _courseRepo.GetAllAsync();
            // In a real app, we'd include Instructor data. With Generic Repo, we might need a specific query method or Include support.
            // For now, let's just return basic info, or fetch instructor manually if needed (N+1 issue but simple for now).
            
            var courseDtos = new List<CourseResponseDto>();
            foreach (var c in courses)
            {
                string instructorName = "Unknown";
                if (c.InstructorId.HasValue)
                {
                    var instructor = await _userRepo.GetByIdAsync(c.InstructorId.Value);
                    instructorName = instructor?.Name ?? "Unknown";
                }
                
                courseDtos.Add(new CourseResponseDto
                {
                    Id = c.Id,
                    Title = c.Title,
                    Description = c.Description,
                    CreditHours = c.CreditHours,
                    InstructorName = instructorName
                });
            }
            return courseDtos;
        }

        public async Task<Course?> CreateCourseAsync(CreateCourseDto courseDto)
        {
            var course = new Course
            {
                Title = courseDto.Title,
                Description = courseDto.Description,
                CreditHours = courseDto.CreditHours,
                InstructorId = courseDto.InstructorId
            };
            
            await _courseRepo.AddAsync(course);
            await _courseRepo.SaveChangesAsync();
            return course;
        }

        public async Task<bool> EnrollStudentAsync(int studentId, int courseId)
        {
            var existing = await _enrollmentRepo.FindAsync(e => e.StudentId == studentId && e.CourseId == courseId);
            if (existing.Any()) return false;

            var enrollment = new Enrollment
            {
                StudentId = studentId,
                CourseId = courseId
            };

            await _enrollmentRepo.AddAsync(enrollment);
            await _enrollmentRepo.SaveChangesAsync();
            return true;
        }

        public async Task<CourseResponseDto?> UpdateCourseAsync(int id, CreateCourseDto courseDto)
        {
            var course = await _courseRepo.GetByIdAsync(id);
            if (course == null) return null;

            course.Title = courseDto.Title;
            course.Description = courseDto.Description;
            course.CreditHours = courseDto.CreditHours;
            course.InstructorId = courseDto.InstructorId;

            _courseRepo.Update(course);
            await _courseRepo.SaveChangesAsync();

            string instructorName = "Unknown";
            if (course.InstructorId.HasValue)
            {
                var instructor = await _userRepo.GetByIdAsync(course.InstructorId.Value);
                instructorName = instructor?.Name ?? "Unknown";
            }

            return new CourseResponseDto
            {
                Id = course.Id,
                Title = course.Title,
                Description = course.Description,
                CreditHours = course.CreditHours,
                InstructorName = instructorName
            };
        }

        public async Task<bool> DeleteCourseAsync(int id)
        {
            var course = await _courseRepo.GetByIdAsync(id);
            if (course == null) return false;

            _courseRepo.Remove(course);
            await _courseRepo.SaveChangesAsync();
            return true;
        }
    }
}
