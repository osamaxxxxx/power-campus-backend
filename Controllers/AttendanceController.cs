using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using webBackendGP.DTOs;
using webBackendGP.Hubs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class AttendanceController : ControllerBase
    {
        private readonly IAttendanceService _attendanceService;
        private readonly IHubContext<AttendanceHub> _hubContext;

        public AttendanceController(IAttendanceService attendanceService, IHubContext<AttendanceHub> hubContext)
        {
            _attendanceService = attendanceService;
            _hubContext = hubContext;
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

            // Broadcast real-time update
            await _hubContext.Clients.All.SendAsync("AttendanceMarked", attendance);

            return Ok(attendance);
        }

        [HttpPost("session/start")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<IActionResult> StartSession(SessionStartDto sessionStartDto)
        {
            // Broadcast session started
            await _hubContext.Clients.All.SendAsync("SessionStarted", sessionStartDto);
            return Ok(new { message = "Session started" });
        }

        [HttpPost("session/stop")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<IActionResult> StopSession()
        {
            // Broadcast session ended
            await _hubContext.Clients.All.SendAsync("SessionEnded");
            return Ok(new { message = "Session stopped" });
        }
    }
}
