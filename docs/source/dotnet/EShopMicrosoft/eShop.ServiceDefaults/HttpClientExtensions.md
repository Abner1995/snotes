# HttpClientExtensions

## 核心功能
1. 自动令牌传递：自动从当前 HTTP 上下文中获取访问令牌，并将其附加到所有通过该 HttpClient 发起的请求中。
2. 简化配置：通过扩展方法 AddAuthToken() 提供简洁的配置方式。


## 使用场景
- 这个扩展主要用于微服务架构中服务间调用的认证场景。例如：
    1. 前端调用后端API：WebApp 调用 IdentityAPI 时自动传递令牌
    2. 服务间调用：OrderingAPI 调用 CatalogAPI 时传递认证信息

```csharp
// 在服务配置中
services.AddHttpClient<ICatalogService, CatalogService>()
    .AddAuthToken();  // 自动添加认证处理

// 在服务类中
public class SomeService
{
    private readonly HttpClient _httpClient;
    
    public SomeService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }
    
    public async Task CallSecuredApi()
    {
        // 不需要手动添加令牌，处理程序会自动处理
        var response = await _httpClient.GetAsync("/api/secured");
    }
}
```  