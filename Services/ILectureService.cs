using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface ILectureService
    {
        Task<IEnumerable<LectureResponseDto>> GetCourseLecturesAsync(int courseId);
        Task<LectureResponseDto?> GetLectureByIdAsync(int id);
        Task<LectureResponseDto> CreateLectureAsync(CreateLectureDto lectureDto);
        Task<LectureResponseDto?> UpdateLectureAsync(int id, CreateLectureDto lectureDto);
        Task<bool> DeleteLectureAsync(int id);
    }
}
