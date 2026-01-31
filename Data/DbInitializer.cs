using webBackendGP.Models;
using webBackendGP.Data;
using BCrypt.Net;

namespace webBackendGP.Data
{
    public static class DbInitializer
    {
        public static void Initialize(AppDbContext context)
        {
            context.Database.EnsureCreated();

            // Look for any users.
            if (context.Users.Any(u => u.Role == UserRole.Admin))
            {
                return;   // DB has been seeded with admin
            }

            var admin = new User
            {
                Name = "System Administrator",
                Email = "admin@university.edu",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin@123"),
                Role = UserRole.Admin
            };

            context.Users.Add(admin);
            context.SaveChanges();
        }
    }
}
