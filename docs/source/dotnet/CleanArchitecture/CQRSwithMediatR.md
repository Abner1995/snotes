# CQRS with MediatR  

## 简介  
1. 职责分离：CQRS 将读取和写入操作分开，避免它们混在一起。命令（Commands）只关注数据的更改，查询（Queries）只关注数据的读取，这样可以更清晰地管理业务逻辑。  
2. 解耦：使用 MediatR 可以解耦各个组件之间的直接依赖。MediatR 充当了一个中介者，接收请求并将其转发到相应的处理器。这样，Controller 不再直接依赖于具体的业务逻辑实现，而是通过 MediatR 发送命令或查询，接收响应。  
3. 可扩展性：随着系统需求的增长，CQRS 架构使得可以根据不同的需求扩展读取和写入操作。例如，查询操作可能会涉及复杂的聚合或者缓存策略，而命令操作可能涉及复杂的事务和状态变更。CQRS 可以让这些两者的扩展更加独立，避免了对现有功能的修改。  
4. 性能优化：由于读取操作和写入操作的职责分开，你可以对查询部分进行更细粒度的优化，比如缓存、只读数据库、或者特殊的查询模型，而写入部分则可以专注于数据一致性和事务。  
5. 简化测试：通过 MediatR 和 CQRS，测试变得更加简单，因为每个命令和查询都有单独的处理逻辑，便于独立测试。你不再需要担心读取和写入逻辑混在一起所带来的复杂性。  
   
举个例子，假设你有一个电商平台，想要查询用户的订单列表和创建新订单。使用 CQRS 后，你可以把查询订单的操作与创建订单的操作分开，查询操作可能是只读的且可以优化缓存，而创建订单则需要考虑事务和数据一致性。  
简单来说，CQRS 和 MediatR 在 WebAPI 中的作用就是帮助开发者保持代码的简洁、模块化，同时提升系统的可维护性和可扩展性。  

## 接下来进行重构CreateRestaurant方法    

```bash  
Install-Package MediatR -Version 12.4.1  
```  

1. 新建CreateRestaurantCommand.cs、CreateRestaurantCommandHandler.cs、CreateRestaurantCommandValidator.cs
```csharp  
using MediatR;

namespace CleanArchitecture.Application.Restaurants.Commands.CreateRestaurant;

public class CreateRestaurantCommand : IRequest<int>
{
    public string Name { get; set; } = default!;
    public string Description { get; set; } = default!;
    public string Category { get; set; } = default!;
    public bool HasDelivery { get; set; }
    public string? ContactEmail { get; set; }
    public string? ContactNumber { get; set; }
    public string? City { get; set; }
    public string? Street { get; set; }
    public string? PostalCode { get; set; }
}
```  

```csharp  
using FluentValidation;

namespace CleanArchitecture.Application.Restaurants.Commands.CreateRestaurant;

public class CreateRestaurantCommandValidator : AbstractValidator<CreateRestaurantCommand>
{
    private readonly List<string> validCategorys = ["蔬菜"];

    public CreateRestaurantCommandValidator()
    {
        RuleFor(x => x.Name).Length(2, 100);

        //自定义
        RuleFor(x => x.Category)
            .Must(validCategorys.Contains)
            .WithMessage("分类不对");

        RuleFor(x => x.ContactNumber)
            .NotEmpty()
            .WithMessage("请输入正确手机号码");
    }
}
```  

```csharp  
using AutoMapper;
using CleanArchitecture.Domain.Entities;
using CleanArchitecture.Domain.Repositories;
using MediatR;
using Microsoft.Extensions.Logging;

namespace CleanArchitecture.Application.Restaurants.Commands.CreateRestaurant;

public class CreateRestaurantCommandHandler(ILogger<CreateRestaurantCommandHandler> logger,
    IMapper mapper,
    IRestaurantsRepository restaurantsRepository) : IRequestHandler<CreateRestaurantCommand, int>
{
    public async Task<int> Handle(CreateRestaurantCommand request, CancellationToken cancellationToken)
    {
        logger.LogInformation("新增餐馆");
        var restaurant = mapper.Map<Restaurant>(request);
        int id = await restaurantsRepository.CreateAsync(restaurant);
        return id;
    }
}
```  

2. 修改RestaurantProfile.cs
```csharp  
using AutoMapper;
using CleanArchitecture.Application.Restaurants.Commands.CreateRestaurant;
using CleanArchitecture.Domain.Entities;

namespace CleanArchitecture.Application.Restaurants.Dtos;

public class RestaurantProfile : Profile
{
    public RestaurantProfile()
    {
        //使用MediatR把CreateRestaurantDto改成CreateRestaurantCommand
        CreateMap<CreateRestaurantCommand, Restaurant>()
            .ForMember(d => d.Address, opt => opt.MapFrom(src => new Address()
            {
                City = src.City,
                Street = src.Street,
                PostalCode = src.PostalCode,
            }));

        CreateMap<Restaurant, RestaurantDto>()
            .ForMember(d => d.City, opt => opt.MapFrom(src => src == null ? null : src.Address.City))
            .ForMember(d => d.Street, opt => opt.MapFrom(src => src == null ? null : src.Address.Street))
            .ForMember(d => d.PostalCode, opt => opt.MapFrom(src => src == null ? null : src.Address.PostalCode))
            .ForMember(d => d.Dishes, opt => opt.MapFrom(src => src.Dishes));
    }
}
```  

3. 把MediatR注入到Startup.cs中  
```csharp  
using CleanArchitecture.Application.Restaurants;
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
    }
}
```  

4. 修改RestaurantsController.cs
```csharp
using CleanArchitecture.Application.Restaurants;
using CleanArchitecture.Application.Restaurants.Commands.CreateRestaurant;
using CleanArchitecture.Application.Restaurants.Dtos;
using MediatR;
using Microsoft.AspNetCore.Components.Forms;
using Microsoft.AspNetCore.Mvc;

namespace CleanArchitecture.API.Controllers;

[Route("api/[controller]")]
[ApiController]
public class RestaurantsController(IRestaurantsService restaurantsService, IMediator mediator) : ControllerBase
{
    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        var restaurants = await restaurantsService.GetAllRestaurants();
        return Ok(restaurants);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetId([FromRoute] int id)
    {
        var restaurant = await restaurantsService.GetId(id);
        if (restaurant is null)
            return NotFound();

        return Ok(restaurant);
    }

    [HttpPost]
    public async Task<IActionResult> CreateRestaurant([FromBody] CreateRestaurantCommand command)
    {
        int id = await mediator.Send(command);
        return CreatedAtAction(nameof(GetId), new { id }, null);
    }
}
```  