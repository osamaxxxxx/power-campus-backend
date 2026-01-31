using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class CoursesController : ControllerBase
    {
        private readonly ICourseService _courseService;

        public CoursesController(ICourseService courseService)
        {
            _courseService = courseService;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<CourseResponseDto>>> GetCourses()
        {
            var courses = await _courseService.GetAllCoursesAsync();
            return Ok(courses);
        }

        [HttpGet("available")]
        public async Task<ActionResult<IEnumerable<CourseResponseDto>>> GetAvailableCourses()
        {
            var courses = await _courseService.GetAllCoursesAsync();
            return Ok(courses);
        }

        [HttpPost]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult> CreateCourse(CreateCourseDto courseDto)
        {
            var course = await _courseService.CreateCourseAsync(courseDto);
            return CreatedAtAction(nameof(GetCourses), new { id = course?.Id }, course);
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<CourseResponseDto>> UpdateCourse(int id, CreateCourseDto courseDto)
        {
            var course = await _courseService.UpdateCourseAsync(id, courseDto);
            if (course == null)
                return NotFound("Course not found");

            return Ok(course);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<IActionResult> DeleteCourse(int id)
        {
            var success = await _courseService.DeleteCourseAsync(id);
            if (!success)
                return NotFound("Course not found");

            return Ok(new { message = "Course deleted successfully" });
        }

        [HttpPost("{courseId}/enroll")]
        [Authorize(Roles = "Student")]
        public async Task<IActionResult> Enroll(int courseId)
        {
            var claims = User.FindAll(ClaimTypes.NameIdentifier).ToList();
            claims.AddRange(User.FindAll("sub"));
            claims.AddRange(User.FindAll("id"));

            int studentId = 0;
            bool found = false;

            foreach (var claim in claims)
            {
                if (int.TryParse(claim.Value, out int id))
                {
                    studentId = id;
                    found = true;
                    break;
                }
            }

            if (!found) 
            {
                 // Fallback for debugging if still not found, though unlikely
                return BadRequest("Invalid User ID: Could not find a numeric ID in token claims.");
            }

            var success = await _courseService.EnrollStudentAsync(studentId, courseId);
            if (!success) return BadRequest("Already enrolled or failed to enroll");

            return Ok("Enrolled successfully");
        }
    }
}
