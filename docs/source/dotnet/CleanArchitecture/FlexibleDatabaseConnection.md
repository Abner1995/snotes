# Flexible Database connection  

上一章节Infrastructure设置启动项的，这集章节API设置启动项。采用数据库连接字符串的方式，可以灵活的切换数据库。  

## 在Infrastructure添加扩展类  
```csharp  
using CleanArchitecture.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace CleanArchitecture.Infrastructure.Extensions;

public static class ServiceCollectionExtensions
{
    public static void AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<RestaurantsDbContext>(options => options.UseSqlServer(configuration.GetConnectionString("RestaurantsDb")));
    }
}
```  

## 重写RestaurantsDbContext  
```csharp  
using CleanArchitecture.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace CleanArchitecture.Infrastructure.Persistence;

internal class RestaurantsDbContext : DbContext
{
    public RestaurantsDbContext(DbContextOptions<RestaurantsDbContext> options) : base(options)
    {

    }

    internal DbSet<Restaurant> Restaurants { get; set; }
    internal DbSet<Dish> Dishes { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
        modelBuilder.ApplyConfigurationsFromAssembly(GetType().Assembly);
    }
}
```  

## 在API配置  
- appsettings.json  
```json  
"ConnectionStrings": {
  "RestaurantsDb": "Server=.;Database=restaurant;User ID=sa;Password=123456;TrustServerCertificate=True;"
}
```  
  
- Program.cs  
```csharp  
// other code
builder.Services.AddInfrastructure(builder.Configuration);
// other code
```  

- 安装Microsoft.EntityFrameworkCore.Tools包
```bash
Install-Package Microsoft.EntityFrameworkCore.Tools -Version 8.0.0  
```  

## 运行  
1. 启动项设置API  
2. 程序包管理器设置Infrastructure  
3. 运行Update-Database
4. 查看数据库是否生成  