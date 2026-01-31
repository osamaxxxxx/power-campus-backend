using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace webBackendGP.Models
{
    public class Attendance
    {
        public int Id { get; set; }

        public int StudentId { get; set; }
        [ForeignKey("StudentId")]
        public User? Student { get; set; }

        public int CourseId { get; set; }
        [ForeignKey("CourseId")]
        public Course? Course { get; set; }

        public int? LectureId { get; set; }
        [ForeignKey("LectureId")]
        public Lecture? Lecture { get; set; }

        public DateTime Date { get; set; }

        public bool IsPresent { get; set; }
    }
}
