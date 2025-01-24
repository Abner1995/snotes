# User Context  

## 在CleanArchitecture.Application项目
1. 新建CurrentUser.cs  
```csharp  
namespace CleanArchitecture.Application.Users;

public record CurrentUser(string Id,
    string Email,
    IEnumerable<string> Roles)
{
    public bool IsInRole(string role) => Roles.Contains(role);
}
```  
2. 新建UserContext.cs  
```csharp  
using Microsoft.AspNetCore.Http;
using System.Security.Claims;

namespace CleanArchitecture.Application.Users
{
    public interface IUserContext
    {
        CurrentUser? GetCurrentUser();
    }

    public class UserContext(IHttpContextAccessor httpContextAccessor) : IUserContext
    {
        public CurrentUser? GetCurrentUser()
        {
            var user = httpContextAccessor?.HttpContext?.User;
            if (user == null)
            {
                throw new InvalidOperationException("User context is not present");
            }

            if (user.Identity == null || !user.Identity.IsAuthenticated)
            {
                return null;
            }

            var userId = user.FindFirst(c => c.Type == ClaimTypes.NameIdentifier)!.Value;
            var email = user.FindFirst(c => c.Type == ClaimTypes.Email)!.Value;
            var roles = user.Claims.Where(c => c.Type == ClaimTypes.Role)!.Select(c => c.Value);

            return new CurrentUser(userId, email, roles);
        }
    }
}
```  
3. 修改ServiceCollectionExtensions.cs  
```csharp  
using CleanArchitecture.Application.Restaurants;
using CleanArchitecture.Application.Users;
using FluentValidation;
using FluentValidation.AspNetCore;
using Microsoft.Extensions.DependencyInjection;

namespace CleanArchitecture.Application.Extensions;

public static class ServiceCollectionExtensions
{
    public static void AddApplication(this IServiceCollection services)
    {
        var applicationAssembly = typeof(ServiceCollectionExtensions).Assembly;
        services.AddScoped<IRestaurantsService, RestaurantsService>();
        services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(applicationAssembly));
        services.AddAutoMapper(applicationAssembly);
        services.AddValidatorsFromAssembly(applicationAssembly)
           .AddFluentValidationAutoValidation();

        services.AddScoped<IUserContext, UserContext>();
        //UserContext使用到IHttpContextAccessor所以需要注入
        services.AddHttpContextAccessor();
    }
}
```  
4. 新建UpdateUserDetailsCommand.cs  
```csharp  
using MediatR;

namespace CleanArchitecture.Application.Users.Commands.UpdateUserDetails;

public class UpdateUserDetailsCommand : IRequest
{
    public DateTime? DateOfBirth { get; set; }
    public string? Nationality { get; set; }
}
```  
5. 新建UpdateUserDetailsCommandHandler.cs  
```csharp  
using CleanArchitecture.Domain.Entities;
using CleanArchitecture.Domain.Exceptions;
using MediatR;
using Microsoft.AspNetCore.Identity;
using Microsoft.Extensions.Logging;

namespace CleanArchitecture.Application.Users.Commands.UpdateUserDetails;

public class UpdateUserDetailsCommandHandler(ILogger<UpdateUserDetailsCommandHandler> logger,
    IUserContext userContext,
    IUserStore<User> userStore) : IRequestHandler<UpdateUserDetailsCommand>
{
    public async Task Handle(UpdateUserDetailsCommand request, CancellationToken cancellationToken)
    {
        var user = userContext.GetCurrentUser();

        logger.LogInformation("Updating user: {UserId}, with {@Request}", user!.Id, request);

        var dbUser = await userStore.FindByIdAsync(user!.Id, cancellationToken);

        if (dbUser == null)
        {
            throw new NotFoundException(nameof(User), user!.Id);
        }

        dbUser.Nationality = request.Nationality;
        dbUser.DateOfBirth = request.DateOfBirth;

        await userStore.UpdateAsync(dbUser, cancellationToken);
    }
}
```  

## 在CleanArchitecture.Domain项目  
1. 修改User.cs  
```csharp  
using Microsoft.AspNetCore.Identity;

namespace CleanArchitecture.Domain.Entities;

public class User : IdentityUser
{
    public DateTime? DateOfBirth { get; set; }
    public string? Nationality { get; set; }
}
```  
2. 在程序包管理器控制台依次执行以下命令执行迁移，查看数据库表结构  
```bash  
Add-Migration  AddUserNationality 
Update-Database  
```  

## 在CleanArchitecture.API项目  
1. 新建IdentityController.cs控制器  
```csharp  
using CleanArchitecture.Application.Users.Commands.UpdateUserDetails;
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CleanArchitecture.API.Controllers;

[ApiController]
[Route("api/identity")]
public class IdentityController(IMediator mediator) : ControllerBase
{
    [HttpPatch("user")]
    [Authorize]
    public async Task<IActionResult> UpdateUserDetails(UpdateUserDetailsCommand command)
    {
        await mediator.Send(command);
        return NoContent();
    }
}
```  

运行项目，请求API是否更新用户的Nationality和DateOfBirth成功  