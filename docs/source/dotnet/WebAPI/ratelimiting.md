# 速率限制

## 安装AspNetCoreRateLimit包

二选一即可  

### 命令行
```bash  
dotnet add package AspNetCoreRateLimit  
```  

### Nuget包管理器  
```bash  
Install-Package AspNetCoreRateLimit  
````  

## 配置appsettings.json  
```json  
{
  "IpRateLimiting": {
    "EnableEndpointRateLimiting": true,
    "StackBlockedRequests": false,
    "RealIpHeader": "X-Real-IP",
    "ClientIdHeader": "X-ClientId",
    "HttpStatusCode": 429,
    "GeneralRules": [
      {
        "Endpoint": "*",
        "Period": "2s",
        "Limit": 5
      }
    ]
  }
}
```  

## 在Program.cs配置  
```csharp 
// ... other code  
builder.Services.AddMemoryCache();
builder.AddRateLimitServices();
// ... other code  

app.UseIpRateLimiting();
```  

### 创建AddRateLimitServices类  
```csharp  
using AspNetCoreRateLimit;

namespace Learn.WebAPI.StartupConfig;

public static class ServicesConfig
{
    public static void AddRateLimitServices(this WebApplicationBuilder builder)
    {
        builder.Services.Configure<IpRateLimitOptions>(
        builder.Configuration.GetSection("IpRateLimiting"));
        builder.Services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
        builder.Services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
        builder.Services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
        builder.Services.AddSingleton<IProcessingStrategy, AsyncKeyLockProcessingStrategy>();
        builder.Services.AddInMemoryRateLimiting();
    }
}
```  

### News控制器使用  
```csharp  
[HttpGet]
public string Get()
{
    return "News";
}
``` 