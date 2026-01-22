using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class GradesController : ControllerBase
    {
        private readonly IGradeService _gradeService;

        public GradesController(IGradeService gradeService)
        {
            _gradeService = gradeService;
        }

        [HttpGet("student/{id}")]
        public async Task<ActionResult<IEnumerable<GradeResponseDto>>> GetStudentGrades(int id)
        {
            var grades = await _gradeService.GetStudentGradesAsync(id);
            return Ok(grades);
        }

        [HttpGet("course/{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<IEnumerable<GradeResponseDto>>> GetCourseGrades(int id)
        {
            var grades = await _gradeService.GetCourseGradesAsync(id);
            return Ok(grades);
        }

        [HttpPost]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<GradeResponseDto>> SubmitGrade(CreateGradeDto gradeDto)
        {
            var grade = await _gradeService.SubmitGradeAsync(gradeDto);
            if (grade == null)
                return BadRequest("Failed to submit grade");

            return CreatedAtAction(nameof(GetStudentGrades), new { id = gradeDto.StudentId }, grade);
        }
    }
}
