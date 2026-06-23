# CreatFlow Server 层设计笔记

## 定位

Server 是**入口和编排层**，不是业务逻辑层。它只做三件事：

1. 收请求（Controller）
2. 调 Application 层的 Service
3. 返回 HTTP 状态码

**Server 不知道数据库怎么实现、不知道密码用什么算法、不知道业务规则。所有它需要的，都由 Infrastructure + Application 提供。**

---

## 依赖关系

```
Server
 ├── Infrastructure  →  Application  →  Domain
 └── (传递拿到) Application + Domain
```

Server 只引用 `CreatFlow.Infrastructure`，通过两行扩展方法接入全部功能：

```csharp
builder.Services.AddInfrastructure(builder.Configuration)  // 仓库/哈希/JWT
    .AddApiServices(builder.Configuration);                // OpenAPI/Scalar
```

---

## 文件结构

```
CreatFlow.Server/
├── CreatFlow.Server.csproj      ← Web SDK, 引 Infrastructure + Scalar.AspNetCore
├── Program.cs                   ← 启动入口，4 段式管道
├── appsettings.json             ← 生产配置（连接串 + JWT Secret）
├── appsettings.Development.json ← 开发覆盖（dev-前缀 JWT 隔离）
├── DependencyInjection.cs       ← Server 自己的 DI 扩展（AddApiServices / UseApiServices）
├── Properties/
│   └── launchSettings.json      ← 调试端口 (http://localhost:5079)
└── Controllers/
    └── AuthController.cs        ← POST /api/auth/{login|register|change-password}
```

---

## Program.cs 设计

.NET 10 Minimal Hosting 的 4 段式模板：

```csharp
// 1. 创建 Builder
var builder = WebApplication.CreateBuilder(args);

// 2. 注册服务（一行接入基础设施 + API 服务）
builder.Services.AddControllers();
builder.Services.AddInfrastructure(builder.Configuration)
    .AddApiServices(builder.Configuration);

// 3. 构建 App
var app = builder.Build();

// 4. 配置中间件管道
app.UseApiServices();                      // Scalar UI (dev only)
app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

// 启动时自动建表（学习阶段，生产应改 Migration）
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

app.Run();
```

### 为什么用 EnsureCreated 而不是 Migration

| 方式 | 适用 |
|------|------|
| `EnsureCreated()` | 学习/V1 阶段，每次启动检查并建表，不用手动迁移 |
| `dotnet ef migrations add` | 生产环境，版本化增量变更 |

学习阶段 `EnsureCreated()` 足够——数据库结构变就删库重来。

---

## DependencyInjection.cs（Server 自有 DI 扩展）

将 OpenAPI/Scalar 的注册和中间件收拢到一个类里，Program.cs 保持简洁：

```csharp
public static class DependencyInjection
{
    public static IServiceCollection AddApiServices(this IServiceCollection services, IConfiguration config)
    {
        services.AddOpenApi(options =>
        {
            // 配置 OpenAPI 文档的元信息
            options.AddDocumentTransformer((doc, ctx, ct) =>
            {
                doc.Info.Title = "CreatFlow API";
                doc.Info.Version = "v1";
                return Task.CompletedTask;
            });
        });
        return services;
    }

    public static WebApplication UseApiServices(this WebApplication app)
    {
        if (app.Environment.IsDevelopment())
        {
            app.MapOpenApi();                    // /openapi/v1.json
            app.MapScalarApiReference(options =>  // /scalar/v1
            {
                options.Title = "CreatFlow API";
                options.Theme = ScalarTheme.Purple;
            });
        }
        return app;
    }
}
```

**设计要点**：

- `AddApiServices` 返回 `IServiceCollection` — 支持链式调用
- `UseApiServices` 返回 `WebApplication` — 同上
- Scalar UI 只在 Development 环境启用 — 生产不暴露 API 文档
- 紫色主题（`ScalarTheme.Purple`）匹配 ClipBridge 的品牌色

---

## AuthController 设计

```csharp
[ApiController]
[Route("api/auth")]
public class AuthController(IAuthService _auth) : ControllerBase
{
    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginCommand cmd, CancellationToken ct)
    {
        var result = await _auth.LoginAsync(cmd, ct);
        return result.Success ? Ok(result) : Unauthorized(result);
    }
    // register, change-password 同理
}
```

### 设计原则

**1. Controller 零业务逻辑**

```csharp
// ✅ Controller 只做路由 + HTTP 映射
return result.Success ? Ok(result) : Unauthorized(result);

// ❌ 不应出现在 Controller 里
if (user.IsExpired()) ...     // 业务判断 → Application 层
var hash = BCrypt.Hash(pwd);  // 密码操作 → Infrastructure 层
```

**2. 用 Result 模式而不是异常**

```csharp
// LoginResult { Success, Token, Error, Member }
// Controller 根据 Success 决定返回 200 还是 401
// 不用 throw new UnauthorizedException()
```

**3. 主构造函数注入**

```csharp
// C# 12 主构造函数 = 等价于构造注入，省 3 行
public class AuthController(IAuthService _auth) : ControllerBase
```

---

## 配置管理

### appsettings.json（生产）

```json
{
  "ConnectionStrings": {
    "Default": "Server=...;Database=creatflow;..."
  },
  "Jwt": {
    "Secret": "<32字节 Base64>",
    "Issuer": "CreatFlow",
    "Audience": "CreatFlow",
    "ExpireDays": 7
  }
}
```

### appsettings.Development.json（开发）

```json
{
  "Jwt": {
    "Secret": "dev-<32字节 Base64>",
    "Issuer": "CreatFlow.Dev",
    "Audience": "CreatFlow.Dev"
  }
}
```

### 为什么分两个文件

- `appsettings.json` — 默认值，生产部署时用环境变量覆盖敏感信息
- `appsettings.Development.json` — 自动覆盖，`dev-` 前缀的 JWT 不会和正式环境混淆

---

## API 文档方案：Scalar

### 为什么不用 Swagger

.NET 9+ 开始，微软推荐 **Scalar** 替代 Swashbuckle（Swagger UI）：

| | Swashbuckle | Scalar |
|---|---|---|
| 维护方 | 社区 | 微软推荐 + 独立团队 |
| .NET 10 原生支持 | ❌ | ✅ |
| UI 体验 | 传统 | 现代化，交互式测试更方便 |
| 包名 | `Swashbuckle.AspNetCore` | `Scalar.AspNetCore` |

### 访问地址

```
启动 Server 后：
  OpenAPI JSON:  http://localhost:5079/openapi/v1.json
  Scalar UI:     http://localhost:5079/scalar/v1
```

---

## 启动验证流程

完整的自检步骤：

```
1. 确保 MySQL 运行，creatflow 数据库已建

2. dotnet run --project src/CreatFlow.Server

3. 观察控制台：
   ✅ Now listening on: http://localhost:5079
   ✅ CREATE TABLE `x_members` ... (首次运行自动建表)
   ✅ Application started.

4. 浏览器打开 http://localhost:5079/scalar/v1
   → 看到 3 个 Auth 端点

5. Scalar UI 中调 POST /api/auth/register 测试
   → 注册成功返回 JWT

6. 调 POST /api/auth/login 测试
   → 登录成功返回 JWT

7. 调 POST /api/auth/change-password 测试
   → 改密成功
```

---

## 依赖注入注册清单

Server 启动时注册的全部服务：

| 服务 | 来源 | 注册方式 |
|------|------|---------|
| `AppDbContext` | Infrastructure | `AddInfrastructure` → `AddDbContext<AppDbContext>` |
| `IMemberRepository` | Infrastructure | `AddInfrastructure` → `AddScoped<IMemberRepository, MemberRepository>` |
| `IPasswordHasher` | Infrastructure | `AddInfrastructure` → `AddScoped<IPasswordHasher, PasswordHasher>` |
| `IJwtService` | Infrastructure | `AddInfrastructure` → `AddScoped<IJwtService, JwtService>` |
| `IAuthService` | Application | `AddInfrastructure` → `AddScoped<IAuthService, AuthService>` |
| OpenAPI | Server | `AddApiServices` → `AddOpenApi()` |
| Controllers | ASP.NET Core | `AddControllers()` |

Server 的 Program.cs 不需要知道任何具体实现类 —— 全部由两行扩展方法完成。

---

## 易错点

1. **忘记 `using CreatFlow.Server`** — `AddApiServices` / `UseApiServices` 是扩展方法，需要 using 所在命名空间
2. **忘记引 Infrastructure 项目** — Server 只引了 Infrastructure，Domain 和 Application 通过传递引用可用
3. **Jwt:Secret 短于 32 字节** — HMAC-SHA256 最少 128 bits = 16 字节，推荐 256 bits = 32 字节
4. **EnsureCreated 不会重建已有表** — 删表需要手动 DROP，或 `EnsureDeleted()` + `EnsureCreated()`
5. **HTTPS 重定向警告** — 开发环境用 HTTP 启动会有这个警告，可忽略或禁用 `app.UseHttpsRedirection()`
