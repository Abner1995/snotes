# JWT  

## 安装包  
在CleanArchitecture.Infrastructure中安装  
```bash  
Install-Package Microsoft.AspNetCore.Authentication.JwtBearer -Version 8.0.10  
Install-Package Microsoft.IdentityModel.Tokens -Version 8.5.0  
Install-Package System.IdentityModel.Tokens.Jwt -Version 8.5.0  
```  

## 如何使用
1. 在CleanArchitecture.Domain中新建IJwtService.cs    
```csharp
using Contact.Domain.Entities;
using System.Security.Claims;

namespace Contact.Domain.Repositories;

public interface IJwtService
{
    public string GenerateToken(User user);
    public string GenerateRefreshToken();
    public int GetTokenExpiry();
    public ClaimsPrincipal GetPrincipalFromExpiredToken(string token);
}
```  
2. 在CleanArchitecture.Infrastructure中  
2.1 新建JwtService.cs    
```csharp
using Contact.Domain.Entities;
using Contact.Domain.Repositories;
using Contact.Infrastructure.Constants;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;

namespace Contact.Infrastructure.Repositories;

internal class JwtService(IOptions<JwtSettings> jwtSettings) : IJwtService
{
    public string GenerateToken(User user)
    {
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.UserName)
        };

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSettings.Value.Secret));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: jwtSettings.Value.Issuer,
            audience: jwtSettings.Value.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(jwtSettings.Value.ExpiryInMinutes),
            signingCredentials: credentials
        );
        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public int GetTokenExpiry() 
    {
        return jwtSettings.Value.ExpiryInMinutes;
    }

    public string GenerateRefreshToken()
    {
        var randomNumber = new byte[32];
        using var rng = RandomNumberGenerator.Create();
        rng.GetBytes(randomNumber);
        return Convert.ToBase64String(randomNumber);
    }

    public ClaimsPrincipal GetPrincipalFromExpiredToken(string token)
    {
        var tokenValidationParameters = new TokenValidationParameters
        {
            ValidateAudience = false,
            ValidateIssuer = false,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSettings.Value.Secret)),
            ValidateLifetime = false
        };
        var tokenHandler = new JwtSecurityTokenHandler();
        var principal = tokenHandler.ValidateToken(token, tokenValidationParameters, out var securityToken);
        if (securityToken is not JwtSecurityToken jwtSecurityToken || !jwtSecurityToken.Header.Alg.Equals(SecurityAlgorithms.HmacSha256, StringComparison.InvariantCultureIgnoreCase))
        {
            throw new SecurityTokenException("无效的 Token");
        }
        return principal;
    }
}
``` 
2.1 ServiceCollectionExtensions.cs注入    
```csharp
public static class ServiceCollectionExtensions
{
    public static void AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddScoped<IJwtService, JwtService>();
    }
}
```
3. 在CleanArchitecture.Application中  
3.1 新建CurrentUser.cs    
```csharp
using Microsoft.AspNetCore.Http;
using System.Security.Claims;

namespace Contact.Application.User;

public class CurrentUser : ClaimsPrincipal
{
    public CurrentUser(IHttpContextAccessor contextAccessor) : base(contextAccessor.HttpContext.User) { }

    public int Id => int.Parse(FindFirst(ClaimTypes.NameIdentifier)?.Value);
}
```
3.2 ServiceCollectionExtensions.cs注入  
```csharp
public static class ServiceCollectionExtensions
{
    public static void AddApplication(this IServiceCollection services)
    {
        services.AddSingleton<CurrentUser>();
        services.AddHttpContextAccessor();
    }
}
```
4. 在CleanArchitecture.API中  
4.1 WebApplicationBuilderExtensions.cs注入  
```csharp
public static class WebApplicationBuilderExtensions
{
    public static void AddPresentation(this WebApplicationBuilder builder)
    {
        builder.Services.AddEndpointsApiExplorer();
        builder.Services.AddSwaggerGen(opts =>
        {
            var title = "通讯录整洁架构API";
            var desc = "通讯录整洁架构API";
            var terms = new Uri("http://localhost:5026");
            var license = new OpenApiLicense()
            {
                Name = "MIT"
            };
            var contact = new OpenApiContact()
            {
                Name = "xuzizheng",
                Email = "wan19950504@gmail.com",
                Url = terms,
            };
            opts.SwaggerDoc("v1", new OpenApiInfo
            {
                Version = "v1",
                Title = $"{title} v1",
                Description = desc,
                TermsOfService = terms,
                License = license,
                Contact = contact
            });
            var securityScheme = new OpenApiSecurityScheme()
            {
                Name = "Authorization",
                Description = "JWT Authorization Header info using bearer tokens",
                In = ParameterLocation.Header,
                Type = SecuritySchemeType.Http,
                Scheme = "bearer",
                BearerFormat = "JWT"
            };
            var securityRequirement = new OpenApiSecurityRequirement
            {
                {
                    new OpenApiSecurityScheme
                    {
                        Reference = new OpenApiReference{
                            Type = ReferenceType.SecurityScheme,
                            Id = "bearerAuth"
                        }
                    },
                    new string[] {}
                }
            };
            opts.AddSecurityDefinition("bearerAuth", securityScheme);
            opts.AddSecurityRequirement(securityRequirement);
        });

        builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection("Authentication"));
        builder.Services.AddAuthentication("Bearer")
            .AddJwtBearer(options =>
            {
                options.TokenValidationParameters = new()
                {
                    ValidateIssuer = true,
                    ValidateAudience = true,
                    ValidateIssuerSigningKey = true,
                    ValidIssuer = builder.Configuration.GetSection("Authentication:Issuer").Value,
                    ValidAudience = builder.Configuration.GetSection("Authentication:Audience").Value,
                    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration.GetSection("Authentication:Secret").Value!))
                };
            });
    }
}
```
5. 需要授权的接口  
```csharp
[Route("api/[controller]")]
[ApiController]
[Authorize]
public class ContactsController(IMediator mediator) : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> CreateContact([FromBody] CreateContactCommand command)
    {
        int id = await mediator.Send(command);
        return CreatedAtAction(nameof(GetId), new { id }, null);
    }
}
```

6. 运行并测试是否正常，比如userid是否是当前登录用户id    