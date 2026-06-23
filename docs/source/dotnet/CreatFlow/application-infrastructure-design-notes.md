# CreatFlow Application 层 & Infrastructure 层设计笔记

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      Server 层                           │
│  Controller → IAuthService.LoginAsync(command)           │
│  不知道任何数据库细节，不知道 BCrypt，不知道 JWT 算法       │
└────────────────────────┬────────────────────────────────┘
                         │ 依赖
┌────────────────────────▼────────────────────────────────┐
│                   Application 层                         │
│  定义：Commands / Results / DTOs / 接口                   │
│  AuthService: 用例编排，不碰数据库、不碰密码算法            │
└────────┬───────────────┬───────────────┬────────────────┘
         │ 依赖           │ 依赖           │ 依赖
         ▼                ▼                ▼
┌─────────────────────────────────────────────────────────┐
│                  Infrastructure 层                       │
│  MemberRepository  : EF Core + MySQL                     │
│  PasswordHasher    : BCrypt.Net-Next                     │
│  JwtService        : System.IdentityModel.Tokens.Jwt     │
│  DependencyInjection: 一行 AddInfrastructure(config)      │
└────────────────────────┬────────────────────────────────┘
                         │ 依赖（传递）
┌────────────────────────▼────────────────────────────────┐
│                     Domain 层                             │
│  Member, Username, PasswordHash, IRepository<T>          │
│  零外部依赖，纯 C#                                        │
└─────────────────────────────────────────────────────────┘
```

---

## 一、Application 层设计

### 1.1 定位：用例编排，不包含业务逻辑

Application 层的唯一职责是**把请求翻译成领域操作序列**。

```
Controller 发来一个 LoginCommand
  → AuthService 收到
  → 1. 调 Repository 查用户
  → 2. 调 PasswordHasher 验密码
  → 3. 调 Member.IsExpired() 验过期（领域规则在 Domain！）
  → 4. 调 JwtService 生成 token
  → 5. 返回 LoginResult
```

**Application 层不自己判断密码是否正确、不自己判断是否过期。** 这些判断属于 Domain 层（`Member.IsExpired()`）和 Infrastructure 层（`PasswordHasher.Verify()`）。

### 1.2 文件结构

```
CreatFlow.Application/
├── DTOs/
│   └── MemberDto.cs              ← 对外暴露的数据快照
├── Identity/
│   ├── Commands/                 ← 用例输入
│   │   ├── LoginCommand.cs
│   │   ├── RegisterCommand.cs
│   │   └── ChangePasswordCommand.cs
│   ├── Results/                  ← 用例输出
│   │   ├── LoginResult.cs
│   │   └── RegisterResult.cs
│   └── Services/                 ← 用例编排
│       ├── IAuthService.cs
│       └── AuthService.cs
├── Common/
│   ├── Interfaces/               ← 基础设施抽象
│   │   ├── IMemberRepository.cs
│   │   ├── IPasswordHasher.cs
│   │   └── IJwtService.cs
│   └── Exceptions/
│       └── ApplicationException.cs
└── GlobalUsing.cs
```

### 1.3 为什么 V1 不用 MediatR

| V1（手写） | 以后（MediatR） |
|---|---|
| `IAuthService` → `AuthService` | `IMediator.Send(command)` → `CommandHandler` |
| 直接注入 Repository | Controller 只注入 IMediator |
| 适合 3-5 个用例 | 适合 10+ 个用例 |

V1 只有登录、注册、改密码三个用例，手写接口更直观。当用例数到 ~10 个、开始出现横切关注点（每个 Handler 都写 try-catch 日志）时，引入 MediatR 的 Pipeline Behavior 水到渠成。

### 1.4 接口放在 Application 层的原因

接口（`IMemberRepository`、`IPasswordHasher`、`IJwtService`）定义在 Application 层而非 Domain 层，是因为：

- Domain 层不应该知道"密码需要哈希"（那是基础设施的选择）
- Domain 层不应该知道"需要 JWT"（那是应用层的安全策略）
- `IMemberRepository` 继承自 Domain 的 `IRepository<Member>`，加了 `GetByUsernameAsync`——这是 Application 层特有的查询需求

这就是**模式 A（严格分层）**：Infrastructure 引用 Application，实现 Application 定义的接口。详见 `ddd-project-reference-patterns.md`。

### 1.5 Command / Result 模式

```csharp
// Command: 不可变的输入
public record LoginCommand(string Username, string Password);

// Result: 包含成功/失败/数据
public record LoginResult(bool Success, string? Token, string? Error, MemberDto? Member);
```

**不用异常控制流。** 登录失败不是"异常"，是"预期的业务结果"。Controller 根据 `Success` 决定返回 200 还是 401。

### 1.6 DTO 放顶层而非 Identity/DTOs/

`MemberDto` 放在 `DTOs/` 而非 `Identity/DTOs/`，因为 DTO 是跨上下文的。`VideoDto`、`UploadTaskDto` 都在同一层，不用纠结放哪个上下文下。

---

## 二、Infrastructure 层设计

### 2.1 定位：接口实现 + DI 注册

Infrastructure 层实现 Application 层定义的所有接口，并用一个扩展方法注册到 DI 容器。

```
Application 定义的接口               Infrastructure 的实现
═══════════════════════              ═══════════════════
IMemberRepository                   MemberRepository      (EF Core + MySQL)
IPasswordHasher                     PasswordHasher        (BCrypt.Net-Next)
IJwtService                         JwtService            (System.IdentityModel.Tokens.Jwt)
```

### 2.2 文件结构

```
CreatFlow.Infrastructure/
├── Persistence/
│   ├── AppDbContext.cs             ← EF Core 上下文
│   └── Configurations/
│       └── MemberConfiguration.cs  ← Member → members 表映射
├── Repositories/
│   └── MemberRepository.cs         ← IMemberRepository 实现
├── Auth/
│   ├── PasswordHasher.cs           ← IPasswordHasher 实现
│   └── JwtService.cs               ← IJwtService 实现
├── Extensions/
│   └── DependencyInjection.cs      ← AddInfrastructure() 扩展方法
└── GlobalUsing.cs
```

### 2.3 值对象映射：HasConversion

Domain 层用了强类型值对象（`MemberId`、`Username`、`PasswordHash`），EF Core 默认不认识。用 `HasConversion` 告诉 EF Core 怎么在 CLR 类型和数据库类型之间转换：

```csharp
builder.Property(m => m.Id)
    .HasConversion(
        id => id.Value,           // MemberId → Guid 写入 DB
        guid => MemberId.Of(guid) // Guid → MemberId 从 DB 读出
    )
    .HasColumnType("char(36)");
```

**为什么不用 OwnsOne？** `OwnsOne` 把值对象的属性平铺到同一张表，语法复杂。`HasConversion` 对单一属性的值对象更简洁——本质上 MemberId 就是一个 Guid 的马甲。

### 2.4 Repository 的 SaveChanges 策略（方案 A）

```
写操作（Add/Update/Delete）→ Repository 内部调 SaveChangesAsync()
读操作（GetById/GetByUsername）→ 不调 SaveChanges
```

**为什么 V1 选方案 A？**

| 方案 | 做法 | 事务边界 |
|------|------|---------|
| A（当前） | Repo 内部 Save | 一次操作 = 一个事务 |
| C（以后） | IUnitOfWork 统一 Save | 一个用例 = 一个事务 |

当前只有 Member 一个聚合，不存在跨聚合事务需求。等加了 ActivationCode 聚合，激活码兑换会员时需要同时操作两个聚合，再引入 IUnitOfWork。详见 `iunitofwork-when-to-use.md`。

### 2.5 主构造函数注入

```csharp
// C# 12 主构造函数语法 = 等价于构造函数注入
public class MemberRepository(AppDbContext _db) : IMemberRepository
{
    // _db 自动成为 private 字段
}
```

DI 容器不关心构造函数的写法——它只看参数类型，反射创建实例。用主构造函数省 4 行样板代码。

### 2.6 JwtService 不依赖 IConfiguration

```csharp
// 构造函数收三个字符串，不是 IConfiguration
public JwtService(string secret, string issuer, string audience)
```

**为什么？** 避免 Infrastructure 层依赖 `Microsoft.Extensions.Configuration`。DI 注册时从 config 读取传入：

```csharp
services.AddScoped<IJwtService>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    return new JwtService(
        config["Jwt:Secret"]!,
        config["Jwt:Issuer"] ?? "CreatFlow",
        config["Jwt:Audience"] ?? "CreatFlow");
});
```

### 2.7 DependencyInjection：一行注册全部

```csharp
// Server/Program.cs —— 一行接入所有基础设施
builder.Services.AddInfrastructure(builder.Configuration);
```

Server 层不知道 MemberRepository 存在，不知道 PasswordHasher 用 BCrypt，不知道 JwtService 用 HMAC-SHA256。它只知道"我调了 AddInfrastructure，认证和数据库都能用了"。

---

## 三、异常层次设计

```
BCL Exception
├── DomainException            ← 业务规则违反（Domain 层）
│   "用户名不能少于3个字符"
│   "会员已过期"
│
├── ApplicationException       ← 用例逻辑失败（Application 层）
│   "用户名或密码错误"
│   "账号已被禁用"
│
├── InvalidOperationException  ← 基础设施配置错误（BCL 自带）
│   "连接字符串未配置"
│   "Jwt:Secret 未配置"
│
└── (Server 层全局异常处理器)   ← 统一的 HTTP 状态码映射
    DomainException       → 422 Unprocessable Entity
    ApplicationException  → 400 Bad Request
    UnauthorizedException → 401 Unauthorized
    NotFoundException     → 404 Not Found
    其他                   → 500 Internal Server Error
```

全局异常处理器是 Server 层的事，不属于 Application 或 Infrastructure 的范围。

---

## 四、关键设计决策速查

| 决策 | 选择 | 为什么 |
|------|------|--------|
| 接口放哪 | Application 层 | 模式 A 严格分层，DI 注册最简单 |
| 用不用 MediatR | V1 不用 | 3 个用例不值得，先手写感受痛点 |
| SaveChanges 谁调 | Repo 内部 | V1 单聚合，无跨聚合事务需求 |
| 值对象映射 | HasConversion | MemberId/Username/PasswordHash 都是单一属性 |
| JWT 配置注入 | 构造函数参数 | 避免 Infrastructure 依赖 IConfiguration |
| 构造函数风格 | C# 12 主构造函数 | 少 4 行样板 |
| DTO 位置 | 顶层 DTOs/ | 跨上下文共享 |
