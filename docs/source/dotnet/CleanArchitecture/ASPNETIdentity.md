# ASPNET Identity  

1. 在CleanArchitecture.Domain中安装Microsoft.AspNetCore.Identity.EntityFrameworkCore
```bash  
Install-Package Microsoft.AspNetCore.Identity.EntityFrameworkCore -Version 9.0.1  
```  
2. 在CleanArchitecture.Domain中新建User实体类  
```csharp  
using Microsoft.AspNetCore.Identity;

namespace CleanArchitecture.Domain.Entities;

public class User : IdentityUser
{
}
```  
3. 修改CleanArchitecture.Infrastructure中修改RestaurantsDbContext.cs代码  
```csharp  
using CleanArchitecture.Domain.Entities;
using Microsoft.AspNetCore.Identity.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore;

namespace CleanArchitecture.Infrastructure.Persistence;

internal class RestaurantsDbContext(DbContextOptions<RestaurantsDbContext> options) : IdentityDbContext<User>(options)
{
    internal DbSet<Restaurant> Restaurants { get; set; }
    internal DbSet<Dish> Dishes { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(GetType().Assembly);
    }
}
```  
4. 在CleanArchitecture.API中修改Program.cs代码  
```csharp  
app.MapGroup("api/identity").MapIdentityApi<User>();
```  
5. 在程序包管理器控制台依次执行以下命令执行迁移，查看数据库表结构  
```bash  
Add-Migration  IdentityAdd  
Update-Database  
```  
6. 运行程序，访问http://localhost:5000/api/identity/register，使用Postman发送请求，注册一个用户   
   1. 如果一开始项目并没有配置Swagger，需要配置，不然没有  
   2. 在CleanArchitecture.API中修改Program.cs代码   
   ```csharp   
   builder.Services.AddEndpointsApiExplorer();
   ```  

7. 在CleanArchitecture.API中新建WebApplicationBuilderExtensions.cs
单独抽离出来  
```csharp   
using CleanArchitecture.API.Middlewares;
using Microsoft.OpenApi.Models;
using Serilog;

namespace CleanArchitecture.API.Extensions;

public static class WebApplicationBuilderExtensions
{
    public static void AddPresentation(this WebApplicationBuilder builder)
    {
        builder.Services.AddControllers();
        builder.Services.AddSwaggerGen(c =>
        {
            c.AddSecurityDefinition("bearerAuth", new OpenApiSecurityScheme
            {
                Type = SecuritySchemeType.Http,
                Scheme = "Bearer"
            });

            c.AddSecurityRequirement(new OpenApiSecurityRequirement
            {
                {
                    new OpenApiSecurityScheme
                    {
                        Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "bearerAuth"}
                    },
                    []
                }

            });
        });
        builder.Services.AddEndpointsApiExplorer();

        builder.Services.AddScoped<ErrorHandlingMiddleware>();
        builder.Services.AddScoped<RequestTimeLoggingMiddleware>();

        builder.Host.UseSerilog((context, configuration) =>
            configuration.ReadFrom.Configuration(context.Configuration)
        );
    }
}
```  
在CleanArchitecture.API中修改Program.cs代码   
```csharp   
builder.AddPresentation();
```  