# 日志

```csharp
private readonly ILogger<UserController> logger;

public UserController(ILogger<UserController> logger)
{
    this.logger = logger;
}

[HttpGet]
[AllowAnonymous]
public IEnumerable<string> Get()
{
    logger.LogInformation("日志");
    return new string[] { "1", "1" };
}
```

