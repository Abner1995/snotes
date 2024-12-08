# Retrieving entities  

:::{seealso}  
- Domain和Application不应该从数据库获取数据    
:::

## 在Application添加RestaurantsService  

### RestaurantsService
```csharp  
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Restaurants;

public interface IRestaurantsService
{
    Task<IEnumerable<Restaurant>> GetAllRestaurants();
    Task<Restaurant?> GetId(int id);
}
```  

```csharp  
using CleanArchitecture.Domain.Entities;
using CleanArchitecture.Domain.Repositories;
using Microsoft.Extensions.Logging;

namespace CleanArchitecture.Application.Restaurants;

internal class RestaurantsService(IRestaurantsRepository restaurantsRepository, ILogger<RestaurantsService> logger) : IRestaurantsService
{
    public Task<IEnumerable<Restaurant>> GetAllRestaurants()
    {
        logger.LogInformation("获取所有餐馆");
        var restaurants = restaurantsRepository.GetAllAsync();
        return restaurants;
    }

    public async Task<Restaurant?> GetId(int id)
    {
        logger.LogInformation($"{id}");
        var restaurant = await restaurantsRepository.GetIdAsync(id);
        return restaurant;
    }
}
```  

### ServiceCollectionExtensions注册IRestaurantsService
```csharp 
using CleanArchitecture.Application.Restaurants;
using Microsoft.Extensions.DependencyInjection;

namespace CleanArchitecture.Application.Extensions;

public static class ServiceCollectionExtensions
{
    public static void AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IRestaurantsService, RestaurantsService>();
    }
}
```  

## 在Domain添加Repositories   
```csharp 
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Domain.Repositories;

public interface IRestaurantsRepository
{
    Task<IEnumerable<Restaurant>> GetAllAsync();
    Task<Restaurant?> GetIdAsync(int id);
}
```  

## 在Infrastructure添加RestaurantsRepository    

### 实现IRestaurantsRepository 
```csharp 
using CleanArchitecture.Domain.Entities;
using CleanArchitecture.Domain.Repositories;
using CleanArchitecture.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace CleanArchitecture.Infrastructure.Repositories;

internal class RestaurantsRepository(RestaurantsDbContext dbContext) : IRestaurantsRepository
{
    public async Task<IEnumerable<Restaurant>> GetAllAsync()
    {
        var Restaurant = await dbContext.Restaurants.ToListAsync();
        return Restaurant;
    }

    public async Task<Restaurant?> GetIdAsync(int id)
    {
        var restaurant = await dbContext.Restaurants.FirstOrDefaultAsync(x => x.Id == id);
        return restaurant;
    }
}
```  

### ServiceCollectionExtensions注册IRestaurantsRepository 
```csharp 
using CleanArchitecture.Domain.Repositories;
using CleanArchitecture.Infrastructure.Persistence;
using CleanArchitecture.Infrastructure.Repositories;
using CleanArchitecture.Infrastructure.Seeders;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace CleanArchitecture.Infrastructure.Extensions;

public static class ServiceCollectionExtensions
{
    public static void AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<RestaurantsDbContext>(options => options.UseSqlServer(configuration.GetConnectionString("RestaurantsDb")));

        services.AddScoped<IRestaurantSeeder, RestaurantSeeder>();
        services.AddScoped<IRestaurantsRepository, RestaurantsRepository>();
    }
}
```  

## 在API配置   
```csharp  
// other code
builder.Services.AddApplication();
// other code
```  

## 新建RestaurantsController   
```csharp  
using CleanArchitecture.Application.Restaurants;
using Microsoft.AspNetCore.Mvc;

namespace CleanArchitecture.API.Controllers;

[Route("api/[controller]")]
[ApiController]
public class RestaurantsController(IRestaurantsService restaurantsService) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var restaurants = await restaurantsService.GetAllRestaurants();
        return Ok(restaurants);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetId([FromRoute]int id)
    {
        var restaurant = await restaurantsService.GetId(id);
        if (restaurant is null)
            return NotFound();

        return Ok(restaurant);
    }
}
```  

运行项目，请求接口    