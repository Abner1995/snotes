# Validation  

用户提交数据到数据库时，需要验证数据的正确性。  
有两种方式，推荐使用Fluent Validation  

## Model Validation  
```csharp  
using System.ComponentModel.DataAnnotations;

namespace CleanArchitecture.Application.Restaurants.Dtos;

public class CreateRestaurantDto
{
    [StringLength(100, MinimumLength = 2)]
    public string Name { get; set; } = default!;
    public string Description { get; set; } = default!;
    public string Category { get; set; } = default!;
    public bool HasDelivery { get; set; }
    public string? ContactEmail { get; set; }
    [Phone(ErrorMessage = "请填写正确号码")]
    public string? ContactNumber { get; set; }
    public string? City { get; set; }
    public string? Street { get; set; }
    public string? PostalCode { get; set; }
}
```  

## Fluent Validation  

1. 安装FluentValidation.AspNetCore
```bash  
Install-Package FluentValidation.AspNetCore -Version 11.3.0
```  
2. 把CreateRestaurantDto的StringLength去掉  
3. 编写CreateRestaurantDtoValidators.cs
```csharp  
using CleanArchitecture.Application.Restaurants.Dtos;
using FluentValidation;

namespace CleanArchitecture.Application.Restaurants.Validators;

public class CreateRestaurantDtoValidators : AbstractValidator<CreateRestaurantDto>
{
    private readonly List<string> validCategorys = ["蔬菜"];

    public CreateRestaurantDtoValidators()
    {
        RuleFor(x => x.Name).Length(2, 100);

        //自定义
        RuleFor(x => x.Category)
            .Must(validCategorys.Contains)
            .WithMessage("分类不对");

        RuleFor(x => x.ContactNumber)
            .EmailAddress()
            .WithMessage("请输入正确手机号码");
    }
}
```   
4. 在Application中的ServiceCollectionExtensions添加FluentValidation  
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
        services.AddAutoMapper(applicationAssembly);
        services.AddValidatorsFromAssembly(applicationAssembly)
           .AddFluentValidationAutoValidation();
    }
}
```  

