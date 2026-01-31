using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class EnrollmentsController : ControllerBase
    {
        private readonly IEnrollmentService _enrollmentService;

        public EnrollmentsController(IEnrollmentService enrollmentService)
        {
            _enrollmentService = enrollmentService;
        }

        [HttpPost]
        public async Task<ActionResult<EnrollmentResponseDto>> EnrollStudent(EnrollmentDto enrollmentDto)
        {
            var enrollment = await _enrollmentService.EnrollStudentAsync(enrollmentDto);
            if (enrollment == null)
                return BadRequest("Student is already enrolled in this course or enrollment failed");

            return CreatedAtAction(nameof(GetStudentCourses), new { id = enrollmentDto.StudentId }, enrollment);
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DropCourse(int id)
        {
            var success = await _enrollmentService.DropCourseAsync(id);
            if (!success)
                return NotFound("Enrollment not found");

            return Ok(new { message = "Course dropped successfully" });
        }

        [HttpGet("students/{id}/courses")]
        public async Task<ActionResult<IEnumerable<EnrollmentResponseDto>>> GetStudentCourses(int id)
        {
            var courses = await _enrollmentService.GetStudentCoursesAsync(id);
            return Ok(courses);
        }

        [HttpGet("course/{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<IEnumerable<EnrollmentResponseDto>>> GetCourseEnrollments(int id)
        {
            var enrollments = await _enrollmentService.GetCourseEnrollmentsAsync(id);
            return Ok(enrollments);
        }
    }
}
