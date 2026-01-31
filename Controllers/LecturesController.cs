using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class LecturesController : ControllerBase
    {
        private readonly ILectureService _lectureService;

        public LecturesController(ILectureService lectureService)
        {
            _lectureService = lectureService;
        }

        [HttpGet("course/{courseId}")]
        public async Task<ActionResult<IEnumerable<LectureResponseDto>>> GetCourseLectures(int courseId)
        {
            var lectures = await _lectureService.GetCourseLecturesAsync(courseId);
            return Ok(lectures);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<LectureResponseDto>> GetLecture(int id)
        {
            var lecture = await _lectureService.GetLectureByIdAsync(id);
            if (lecture == null) return NotFound();
            return Ok(lecture);
        }

        [HttpPost]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<LectureResponseDto>> CreateLecture(CreateLectureDto lectureDto)
        {
            var lecture = await _lectureService.CreateLectureAsync(lectureDto);
            return CreatedAtAction(nameof(GetLecture), new { id = lecture.Id }, lecture);
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<LectureResponseDto>> UpdateLecture(int id, CreateLectureDto lectureDto)
        {
            var lecture = await _lectureService.UpdateLectureAsync(id, lectureDto);
            if (lecture == null) return NotFound();
            return Ok(lecture);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<IActionResult> DeleteLecture(int id)
        {
            var success = await _lectureService.DeleteLectureAsync(id);
            if (!success) return NotFound();
            return NoContent();
        }
    }
}
