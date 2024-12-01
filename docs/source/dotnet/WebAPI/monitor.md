# 监控

:::{note}  
仓库地址 [github](https://github.com/IzyPro/WatchDog)  
:::  

## 配置appsettings.json  
```json  
"WatchDog": {
  "UserName": "",
  "PassWord": ""
}
```  

## 在Program.cs配置  

```csharp 
// ... other code  
builder.Services.AddWatchDogServices();
// ... other code  

var app = builder.Build();

app.UseWatchDogExceptionLogger();

app.UseWatchDog(opt =>
{
    opt.WatchPageUsername = app.Configuration.GetValue<string>("WatchDog:UserName");
    opt.WatchPagePassword = app.Configuration.GetValue<string>("WatchDog:PassWord");
});
```  

## 访问
[WatchDog](http://localhost:5252/WatchDog)  

:::{note}  
1. 由于添加了JWT无法访问  
2. 如何配置了WatchDog，其他控制器标识AllowAnonymous都需要授权了  
:::  

