# 缓存

## 缓存配置  

在Program.cs配置  

```csharp  
// ... other code  
builder.Services.AddResponseCaching();
// ... other code  
```  

## 控制器 
```csharp  
[HttpGet]
[AllowAnonymous]
[ResponseCache(Duration = 10, Location = ResponseCacheLocation.Any, NoStore = false)]
public IEnumerable<string> Get()
{
    logger.LogInformation("日志");
    return new string[] { "1", "1" };
}
```  

### ResponseCacheLocation说明  

1. Duration = 10: 这个参数指定了响应应该被缓存的时间长度，单位是秒。在这个例子中，值为10，意味着响应将被缓存10秒。
2. Location = ResponseCacheLocation.Any: 这个参数定义了响应可以被缓存的位置。ResponseCacheLocation.Any 表示响应可以在任何位置被缓存，包括私有缓存（如用户的浏览器）和公共缓存（如代理服务器）。其他可能的选项包括：
   - None：不指定缓存位置。
   - Client：仅客户端缓存。
   - Server：仅服务器端缓存。
   - ServerAndClient：客户端和服务器都可以缓存。
3. NoStore = false: 这个布尔值参数决定了是否完全禁止存储响应。如果设置为true，则会指示缓存机制不要存储响应。在此例中，值为false，意味着允许缓存响应。  
   
综上所述，这段代码的意思是：当某个请求命中了带有这个属性的方法时，其响应会被缓存10秒钟，并且可以被任何类型的缓存（例如客户端浏览器、代理服务器等）所存储。这有助于减少对服务器的重复请求，提高性能，特别是在处理静态内容或频繁访问但不经常变化的数据时非常有用。