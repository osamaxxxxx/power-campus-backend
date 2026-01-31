using Microsoft.EntityFrameworkCore;
using webBackendGP.Data;
using webBackendGP.DTOs;
using webBackendGP.Models;
using webBackendGP.Repositories;

namespace webBackendGP.Services
{
    public class LectureService : ILectureService
    {
        private readonly IRepository<Lecture> _lectureRepository;
        private readonly AppDbContext _context;

        public LectureService(IRepository<Lecture> lectureRepository, AppDbContext context)
        {
            _lectureRepository = lectureRepository;
            _context = context;
        }

        public async Task<IEnumerable<LectureResponseDto>> GetCourseLecturesAsync(int courseId)
        {
            var lectures = await _context.Lectures
                .Include(l => l.Course)
                .Where(l => l.CourseId == courseId)
                .OrderBy(l => l.Date)
                .ToListAsync();

            return lectures.Select(l => new LectureResponseDto
            {
                Id = l.Id,
                CourseId = l.CourseId,
                CourseName = l.Course?.Title ?? "",
                Title = l.Title,
                Description = l.Description,
                Date = l.Date,
                StartTime = l.StartTime,
                EndTime = l.EndTime
            });
        }

        public async Task<LectureResponseDto?> GetLectureByIdAsync(int id)
        {
            var l = await _context.Lectures
                .Include(l => l.Course)
                .FirstOrDefaultAsync(l => l.Id == id);

            if (l == null) return null;

            return new LectureResponseDto
            {
                Id = l.Id,
                CourseId = l.CourseId,
                CourseName = l.Course?.Title ?? "",
                Title = l.Title,
                Description = l.Description,
                Date = l.Date,
                StartTime = l.StartTime,
                EndTime = l.EndTime
            };
        }

        public async Task<LectureResponseDto> CreateLectureAsync(CreateLectureDto lectureDto)
        {
            var lecture = new Lecture
            {
                CourseId = lectureDto.CourseId,
                Title = lectureDto.Title,
                Description = lectureDto.Description,
                Date = lectureDto.Date,
                StartTime = lectureDto.StartTime,
                EndTime = lectureDto.EndTime
            };

            await _lectureRepository.AddAsync(lecture);
            await _lectureRepository.SaveChangesAsync();

            var saved = await GetLectureByIdAsync(lecture.Id);
            return saved!;
        }

        public async Task<LectureResponseDto?> UpdateLectureAsync(int id, CreateLectureDto lectureDto)
        {
            var lecture = await _lectureRepository.GetByIdAsync(id);
            if (lecture == null) return null;

            lecture.Title = lectureDto.Title;
            lecture.Description = lectureDto.Description;
            lecture.Date = lectureDto.Date;
            lecture.StartTime = lectureDto.StartTime;
            lecture.EndTime = lectureDto.EndTime;
            lecture.CourseId = lectureDto.CourseId;

            _lectureRepository.Update(lecture);
            await _lectureRepository.SaveChangesAsync();

            return await GetLectureByIdAsync(id);
        }

        public async Task<bool> DeleteLectureAsync(int id)
        {
            var lecture = await _lectureRepository.GetByIdAsync(id);
            if (lecture == null) return false;

            _lectureRepository.Remove(lecture);
            await _lectureRepository.SaveChangesAsync();
            return true;
        }
    }
}
