# Exceptions  

全局处理异常，也可以自定义异常  

## Exception Handling middleware  
1. 在CleanArchitecture.API项目中添加以下文件
ErrorHandlingMiddleware.cs  
```csharp  
using CleanArchitecture.Domain.Exceptions;

namespace CleanArchitecture.API.Middlewares;

public class ErrorHandlingMiddleware(ILogger<ErrorHandlingMiddleware> logger) : IMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        try
        {
            await next.Invoke(context);
        }
        catch (NotFoundException notFound)
        {
            context.Response.StatusCode = 404;
            await context.Response.WriteAsync(notFound.Message);

            logger.LogWarning(notFound.Message);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, ex.Message);

            context.Response.StatusCode = 500;
            await context.Response.WriteAsync("Something went wrong");
        }
    }
}
```
RequestTimeLoggingMiddleware.cs  
```csharp  
using System.Diagnostics;

namespace CleanArchitecture.API.Middlewares;

public class RequestTimeLoggingMiddleware(ILogger<RequestTimeLoggingMiddleware> logger) : IMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var stopWatch = Stopwatch.StartNew();
        await next.Invoke(context);
        stopWatch.Stop();

        if (stopWatch.ElapsedMilliseconds / 1000 > 4)
        {
            logger.LogInformation("Request [{Verb}] at {Path} took {Time} ms",
                context.Request.Method,
                context.Request.Path,
                stopWatch.ElapsedMilliseconds);
        }
    }
}
```

2. 在CleanArchitecture.API项目的Program.cs中添加以下代码：
```csharp    
builder.Services.AddScoped<ErrorHandlingMiddleware>();
builder.Services.AddScoped<RequestTimeLoggingMiddleware>();

app.UseMiddleware<ErrorHandlingMiddleware>();
app.UseMiddleware<RequestTimeLoggingMiddleware>();
```  

3. 在CleanArchitecture.Domain中添加以下文件NotFoundException.cs
```csharp  
namespace CleanArchitecture.Domain.Exceptions;

public class NotFoundException(string resourceType, string resourceIdentifier) : Exception($"{resourceType} with id: {resourceIdentifier} doesn't exist")
{

}
```

4. 修改DeleteRestaurantCommandHandler等文件代码，添加以下代码：
```csharp  
if (restaurant is null)
    throw new NotFoundException(nameof(Restaurant), request.Id.ToString());
```