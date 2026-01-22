using webBackendGP.DTOs;

namespace webBackendGP.Services
{
    public interface IUserService
    {
        Task<IEnumerable<UserResponseDto>> GetAllUsersAsync();
        Task<UserResponseDto?> GetUserByIdAsync(int id);
        Task<UserResponseDto?> CreateUserAsync(RegisterDto registerDto);
        Task<UserResponseDto?> UpdateUserAsync(int id, UpdateUserDto updateDto);
        Task<bool> DeleteUserAsync(int id);
    }
}
