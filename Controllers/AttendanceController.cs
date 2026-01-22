using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class AttendanceController : ControllerBase
    {
        private readonly IAttendanceService _attendanceService;

        public AttendanceController(IAttendanceService attendanceService)
        {
            _attendanceService = attendanceService;
        }

        [HttpGet("student/{id}")]
        public async Task<ActionResult<IEnumerable<AttendanceResponseDto>>> GetStudentAttendance(int id)
        {
            var attendance = await _attendanceService.GetStudentAttendanceAsync(id);
            return Ok(attendance);
        }

        [HttpGet("course/{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<IEnumerable<AttendanceResponseDto>>> GetCourseAttendance(int id)
        {
            var attendance = await _attendanceService.GetCourseAttendanceAsync(id);
            return Ok(attendance);
        }

        [HttpPost]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<AttendanceResponseDto>> MarkAttendance(AttendanceDto attendanceDto)
        {
            var attendance = await _attendanceService.MarkAttendanceAsync(attendanceDto);
            if (attendance == null)
                return BadRequest("Failed to mark attendance");

            return Ok(attendance);
        }
    }
}
