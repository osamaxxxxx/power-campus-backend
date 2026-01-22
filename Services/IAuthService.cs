using webBackendGP.DTOs;
using webBackendGP.Models;

namespace webBackendGP.Services
{
    public interface IAuthService
    {
        Task<AuthResponseDto?> LoginAsync(LoginDto loginDto);
        Task<User?> RegisterAsync(RegisterDto registerDto);
    }
}
