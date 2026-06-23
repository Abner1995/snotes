# DDD 类库引用模式

.NET DDD 项目三层（Domain / Application / Infrastructure）之间的三种引用方式。

---

## 模式 A: 严格分层（CreatFlow 当前使用）

接口放在 **Application 层**，Infrastructure 引用 Application。

```
Domain              ← 零依赖
  ↑
Application        ← 只引 Domain
  ↑
Infrastructure     ← 只引 Application（Domain 自动传递）
```

```xml
<!-- Domain.csproj -->
<!-- (无 ProjectReference) -->

<!-- Application.csproj -->
<ProjectReference Include="..\CreatFlow.Domain\CreatFlow.Domain.csproj" />

<!-- Infrastructure.csproj -->
<ProjectReference Include="..\CreatFlow.Application\CreatFlow.Application.csproj" />
```

| 优点 | 缺点 |
|------|------|
| DI 注册简洁：Infrastructure 直接 `AddScoped<IRepo, Repo>()` | Infrastructure 知道了 Application 层 |
| 项目数少（3 个） | 不符合严格的"内层不知外层的"洋葱规则 |
| 适合 V1 / 小项目 | — |

---

## 模式 B: 洋葱架构 (Onion / Hexagonal)

接口放在 **Domain 层**，Infrastructure 只引 Domain。

```
Domain              ← 零依赖，包含所有接口（IRepository、IPasswordHasher 等）
  ↑         ↑
  │         │
Application  Infrastructure  ← 两者都只引 Domain，互不知道
  ↑
  │
Server         ← 引用 Application + Infrastructure，手动绑定 DI
```

```xml
<!-- Domain.csproj -->
<!-- 接口定义在这里: IRepository<T>, IPasswordHasher, IJwtService -->
<!-- (无 ProjectReference) -->

<!-- Application.csproj -->
<ProjectReference Include="..\CreatFlow.Domain\CreatFlow.Domain.csproj" />

<!-- Infrastructure.csproj -->
<ProjectReference Include="..\CreatFlow.Domain\CreatFlow.Domain.csproj" />

<!-- Server.csproj -->
<ProjectReference Include="..\CreatFlow.Application\CreatFlow.Application.csproj" />
<ProjectReference Include="..\CreatFlow.Infrastructure\CreatFlow.Infrastructure.csproj" />
```

Server 负责组装：

```csharp
// Program.cs
builder.Services.AddScoped<IMemberRepository, MemberRepository>();
builder.Services.AddScoped<IPasswordHasher, PasswordHasher>();
```

| 优点 | 缺点 |
|------|------|
| Infrastructure 不依赖 Application，真正独立 | DI 注册必须在 Server 手动写 |
| 符合洋葱架构"内层无外部依赖"原则 | 接口定义在 Domain，Domain 膨胀 |
| 开源项目常用（eshopOnContainers） | — |

---

## 模式 C: Contracts 独立（Clean Architecture）

接口独立为 **Contracts 项目**，Application 和 Infrastructure 都只引它。

```
Domain              ← 零依赖（纯实体、值对象、领域事件）
  ↑
Contracts           ← 只引 Domain（放接口：IRepo、IHasher、IJwt...）
  ↑         ↑
  │         │
Application  Infrastructure  ← 两者都只引 Contracts，互不知道
  ↑
  │
Server         ← 引用 Application + Infrastructure，手动绑定 DI
```

```xml
<!-- Domain.csproj -->
<!-- (无 ProjectReference) -->

<!-- Contracts.csproj -->
<ProjectReference Include="..\CreatFlow.Domain\CreatFlow.Domain.csproj" />

<!-- Application.csproj -->
<ProjectReference Include="..\CreatFlow.Contracts\CreatFlow.Contracts.csproj" />

<!-- Infrastructure.csproj -->
<ProjectReference Include="..\CreatFlow.Contracts\CreatFlow.Contracts.csproj" />

<!-- Server.csproj -->
<ProjectReference Include="..\CreatFlow.Application\CreatFlow.Application.csproj" />
<ProjectReference Include="..\CreatFlow.Infrastructure\CreatFlow.Infrastructure.csproj" />
```

| 优点 | 缺点 |
|------|------|
| Domain 极纯（零接口义务） | 项目数多（4 个） |
| 接口与实现完全物理隔离 | 小项目杀鸡用牛刀 |
| 换 Infrastructure 不影响 Application | — |
| VS / dotnet 新模板默认这种 | — |

---

## 对比总结

| | 模式 A | 模式 B | 模式 C |
|---|---|---|---|
| 接口放哪 | Application | Domain | Contracts |
| Infrastructure 引谁 | Application | Domain | Contracts |
| 项目数 | 3 | 3 | 4 |
| DI 注册写在哪 | Infrastructure 自己 | Server | Server |
| 适合场景 | 学习/V1/小项目 | 中大型项目 | 大型/多实现项目 |

---

## CreatFlow 的选择

当前使用 **模式 A**。原因：

- V1 阶段，用例少，接口少
- Infrastructure 的 `DependencyInjection.cs` 一行注册全部，Server 零配置
- 后续可以迁移到模式 C（把 `Common/Interfaces/` 提取为 `CreatFlow.Contracts`）

迁移成本很低——只是把接口文件挪到一个新项目，改引用路径。
