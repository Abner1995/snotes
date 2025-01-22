# Retrieving DTOs  

## 使用DTO  

在Application添加DTOs的RestaurantDto、DishDto  

### RestaurantDto
```csharp  
using CleanArchitecture.Application.Dishes.Dtos;
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Restaurants.Dtos;

public class RestaurantDto
{
    public int Id { get; set; }
    public string Name { get; set; } = default!;
    public string Description { get; set; } = default!;
    public string Category { get; set; } = default!;
    public bool HasDelivery { get; set; }
    public string? City { get; set; }
    public string? Street { get; set; }
    public string? PostalCode { get; set; }
    public List<DishDto> Dishes { get; set; } = new();

    public static RestaurantDto? FromEntity(Restaurant? r)
    {
        if (r == null) return null;
        return new RestaurantDto()
        {
            Id = r.Id,
            Name = r.Name,
            Description = r.Description,
            Category = r.Category,
            HasDelivery = r.HasDelivery,
            City = r.Address?.City,
            Street = r.Address?.Street,
            PostalCode = r.Address?.PostalCode,
            Dishes = r.Dishes.Select(DishDto.FromEntity).ToList()
        };
    }
}
```  

### DishDto  
```csharp  
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Dishes.Dtos;

public class DishDto
{
    public int Id { get; set; }
    public string Name { get; set; } = default!;
    public string Description { get; set; } = default!;
    public decimal Price { get; set; }
    public int? KiloCalories { get; set; }
    public int RestaurantId { get; set; }

    public static DishDto FromEntity(Dish d)
    {
        return new DishDto()
        {
            Id = d.Id,
            Name = d.Name,
            Description = d.Description,
            Price = d.Price,
            KiloCalories = d.KiloCalories,
        };
    }
}
```  

## IRestaurantsService RestaurantsService

1. 把文件中Restaurant改成RestaurantDto  
2. RestaurantsService代码  
```csharp  
using CleanArchitecture.Application.Restaurants.Dtos;
using CleanArchitecture.Domain.Repositories;
using Microsoft.Extensions.Logging;

namespace CleanArchitecture.Application.Restaurants;

internal class RestaurantsService(IRestaurantsRepository restaurantsRepository, ILogger<RestaurantsService> logger) : IRestaurantsService
{
    public async Task<IEnumerable<RestaurantDto>> GetAllRestaurants()
    {
        logger.LogInformation("获取所有餐馆");
        var restaurants = await restaurantsRepository.GetAllAsync();
        var restaurantsDto = restaurants.Select(RestaurantDto.FromEntity);
        return restaurantsDto!;
    }

    public async Task<RestaurantDto?> GetId(int id)
    {
        logger.LogInformation($"{id}");
        var restaurant = await restaurantsRepository.GetIdAsync(id);
        var restaurantDto = RestaurantDto.FromEntity(restaurant);
        return restaurantDto;
    }
}
```    

## 使用AutoMapper  

```bash  
Install-Package AutoMapper.Extensions.Microsoft.DependencyInjection -Version 12.0.1    
``` 

1. 在Application添加Profile的RestaurantProfile、DishProfile  
```csharp  
using AutoMapper;
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Restaurants.Dtos;

public class RestaurantProfile : Profile
{
    public RestaurantProfile()
    {
        CreateMap<Restaurant, RestaurantDto>()
            .ForMember(d => d.City, opt => opt.MapFrom(src => src == null ? null : src.Address.City))
            .ForMember(d => d.Street, opt => opt.MapFrom(src => src == null ? null : src.Address.Street))
            .ForMember(d => d.PostalCode, opt => opt.MapFrom(src => src == null ? null : src.Address.PostalCode))
            .ForMember(d => d.Dishes, opt => opt.MapFrom(src => src.Dishes));
    }
}
``` 

```csharp  
using AutoMapper;
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Dishes.Dtos;

public class DishProfile : Profile
{
    public DishProfile()
    {
        CreateMap<Dish, DishDto>();
    }
}
``` 

2. 把Profile注入添加到Startup.cs中  
```csharp  
using CleanArchitecture.Application.Restaurants;
using Microsoft.Extensions.DependencyInjection;

namespace CleanArchitecture.Application.Extensions;

public static class ServiceCollectionExtensions
{
    public static void AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IRestaurantsService, RestaurantsService>();
        services.AddAutoMapper(typeof(ServiceCollectionExtensions).Assembly);
    }
}
```  

3. RestaurantsService代码中使用AutoMapper替换      
```csharp  
using AutoMapper;
using CleanArchitecture.Application.Restaurants.Dtos;
using CleanArchitecture.Domain.Repositories;
using Microsoft.Extensions.Logging;

namespace CleanArchitecture.Application.Restaurants;

internal class RestaurantsService(IRestaurantsRepository restaurantsRepository, ILogger<RestaurantsService> logger, IMapper mapper) : IRestaurantsService
{
    public async Task<IEnumerable<RestaurantDto>> GetAllRestaurants()
    {
        logger.LogInformation("获取所有餐馆");
        var restaurants = await restaurantsRepository.GetAllAsync();
        //使用AutoMapper
        var restaurantsDto = mapper.Map<IEnumerable<RestaurantDto>>(restaurants);
        return restaurantsDto!;
    }

    public async Task<RestaurantDto?> GetId(int id)
    {
        logger.LogInformation($"{id}");
        var restaurant = await restaurantsRepository.GetIdAsync(id);
        var restaurantDto = mapper.Map<RestaurantDto?>(restaurant);
        return restaurantDto;
    }
}
```    

运行项目，请求接口    