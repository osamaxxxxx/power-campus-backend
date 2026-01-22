using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using webBackendGP.DTOs;
using webBackendGP.Services;

namespace webBackendGP.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class ScheduleController : ControllerBase
    {
        private readonly IScheduleService _scheduleService;

        public ScheduleController(IScheduleService scheduleService)
        {
            _scheduleService = scheduleService;
        }

        [HttpGet("student/{id}")]
        public async Task<ActionResult<IEnumerable<ScheduleResponseDto>>> GetStudentSchedule(int id)
        {
            var schedule = await _scheduleService.GetStudentScheduleAsync(id);
            return Ok(schedule);
        }

        [HttpGet("doctor/{id}")]
        public async Task<ActionResult<IEnumerable<ScheduleResponseDto>>> GetInstructorSchedule(int id)
        {
            var schedule = await _scheduleService.GetInstructorScheduleAsync(id);
            return Ok(schedule);
        }

        [HttpPost]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<ScheduleResponseDto>> CreateSchedule(ScheduleDto scheduleDto)
        {
            var schedule = await _scheduleService.CreateScheduleAsync(scheduleDto);
            if (schedule == null)
                return BadRequest("Failed to create schedule");

            return CreatedAtAction(nameof(GetStudentSchedule), new { id = schedule.Id }, schedule);
        }

        [HttpPut("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<ActionResult<ScheduleResponseDto>> UpdateSchedule(int id, ScheduleDto scheduleDto)
        {
            var schedule = await _scheduleService.UpdateScheduleAsync(id, scheduleDto);
            if (schedule == null)
                return NotFound("Schedule not found");

            return Ok(schedule);
        }

        [HttpDelete("{id}")]
        [Authorize(Roles = "Admin,Instructor")]
        public async Task<IActionResult> DeleteSchedule(int id)
        {
            var success = await _scheduleService.DeleteScheduleAsync(id);
            if (!success)
                return NotFound("Schedule not found");

            return Ok(new { message = "Schedule deleted successfully" });
        }
    }
}
