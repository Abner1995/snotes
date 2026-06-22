# CreatFlow.Domain — DDD 领域层设计笔记

> 这些笔记以 CreatFlow 项目的 Domain 层为实例，逐一解释 DDD 中用到的核心概念：充血模型、聚合根、值对象、领域事件等。

---

## 1. 贫血模型 vs 充血模型

这是 DDD 里最容易被忽视、但也最关键的决策。Martin Fowler 在 2003 年就指出贫血模型是反模式，但大多数 .NET 项目仍然在用。

### 贫血模型

特征是：**类只存数据，没有行为**。所有业务逻辑写在 Service 层。

```csharp
// 贫血的 Member —— 一个数据袋
public class Member
{
    public int Id { get; set; }
    public string Username { get; set; }
    public string PasswordHash { get; set; }
    public DateTime ExpireDate { get; set; }
    public bool IsActive { get; set; }
}

// 业务规则在外面的 Service 里
public class MemberService
{
    public void DisableMember(Member member)
    {
        if (!member.IsActive) return;      // 规则1: 已禁用的跳过
        member.IsActive = false;            // 规则2: 改状态
        _auditLog.Write(...);               // 规则3: 记录日志
    }

    public void ExtendMember(Member member, int days)
    {
        if (days <= 0) throw ...;          // 规则1: 天数必须 > 0
        member.ExpireDate = member.ExpireDate.AddDays(days);  // 规则2
    }
}
```

这段代码能跑，但有三个隐患：

1. **Service 必须知道 Member 的内部细节** — 如何判断"已禁用"、ExpireDate 怎么算延期，这些本来应该是 Member 自己的知识
2. **谁都能绕过规则** — 另一个 Service 里写 `member.IsActive = true` 就跳过禁用了，因为 setter 是 public 的
3. **改规则要全局搜索** — 如果"禁用"逻辑要加一条"同时失效所有 session"，你得在所有改 `IsActive` 的地方加代码

### 充血模型

特征是：**数据和行为封装在一起，外部只能通过方法操作**。

CreatFlow 的 `Member.cs` 就是这样写的：

```csharp
// 充血的 Member —— 行为和数据在一起
public class Member : Aggregate<MemberId>
{
    public Username Username { get; private set; } = default!;
    public PasswordHash PasswordHash { get; private set; } = default!;
    public DateTime ExpireDate { get; private set; }
    public bool IsActive { get; private set; } = true;

    // private set + 领域方法 = 外部不能直接改属性

    public void Disable()
    {
        if (!IsActive) return;
        IsActive = false;
        AddDomainEvent(new MemberDisabledEvent(Id));
    }

    public void Extend(int days)
    {
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(days);
        ExpireDate = ExpireDate.AddDays(days);
        AddDomainEvent(new MemberExtendedEvent(Id, ExpireDate));
    }

    public bool IsExpired() => DateTime.UtcNow > ExpireDate;
}
```

用法对比：

```csharp
// ✅ 充血 — 调方法，不让改属性
member.Disable();

// ❌ 编译不过 — private set
member.IsActive = false;
```

**充血模型的核心思想：不要让外部代码替实体做决策。** Member 自己最清楚怎么禁用自己、怎么算延期。Service 只是协调者，不是决策者。

### 这个项目为什么用充血

| 理由 | 说明 |
|------|------|
| 业务规则集中 | 会员生命周期（到期、禁用、续费）本身就复杂，应该待在 Member 里 |
| `private set` 防呆 | 编译器帮你挡错误，比 code review 可靠 |
| DDD 需要它 | 聚合根、领域事件这些概念都建立在充血模型上。贫血模型不需要聚合根 |

### 贫血模型什么时候可以

- 纯 CRUD — 没有业务规则，只是读/写数据库
- 配置表 — 改动量 `is_active`、改个 `display_order` 这种简单操作
- 原型验证 — 先跑通流程再重构

CreatFlow 有明显的领域规则（会员到期、激活码兑换、平台风控调度），充血模型更匹配。

---

## 2. 为什么需要 IAggregate / Aggregate 体系

### 整体继承结构

```
IEntity              ← "我是实体，我有 Id"
    ↑
IEntity<T>            ← "我的 Id 类型是 T"（编译期类型安全）
    ↑
Entity<T>              ← 基类: 提供 Id + 审计字段的实现
    ↑
IAggregate             ← "我是聚合根，我能持有领域事件"
    ↑
IAggregate<T>
    ↑
Aggregate<T>           ← 基类: 提供领域事件的收集/清理机制
    ↑
Admin / Member         ← 实际业务类，继承 Aggregate<T>
```

这个结构看起来复杂，但每多一层都解决一个具体问题。

### 问题一：为什么 Id 是泛型 T，不是 int？

```csharp
// 如果写死 int Id
public abstract class Entity
{
    public int Id { get; set; }
}

// 隐患: 任何 int 都能当 Id 用
var member = repo.GetById(1);  // 这个 1 是 MemberId 还是 AdminId？
DeleteUser(1);                  // 不小心传了 AdminId，编译器不知道
```

泛型 Id 解决这个问题：

```csharp
// Entity 基类
public abstract class Entity<T> : IEntity<T>
{
    public T Id { get; set; } = default!;
}

// Admin 的 Id 类型是 AdminId
public class Admin : Aggregate<AdminId> { }

// Member 的 Id 类型是 MemberId
public class Member : Aggregate<MemberId> { }

// 编译期强制类型匹配
_repo.GetAdminById(memberId);   // ❌ 编译错误 — 不能把 MemberId 当 AdminId
```

### 问题二：为什么需要 IAggregate 接口？基类不够吗？

两个用处：

**1) 基础设施层统一遍历所有聚合根**

未来 EF Core SaveChanges 时，需要从所有聚合根中提取领域事件然后发布。如果有接口：

```csharp
// EF Core 拦截器 — 遍历所有实现 IAggregate 的实体
foreach (var entry in context.ChangeTracker.Entries<IAggregate>())
{
    var events = entry.Entity.ClearDomainEvents();
    foreach (var e in events) { /* 发布 */ }
}
```

没有接口的话，每新增一个聚合根就要改这里：

```csharp
// ❌ 加一个聚合根加一行
.Entries<Admin>()
.Entries<Member>()
.Entries<ActivationCode>()  // 新加的
```

**2) 仓储泛型约束**

```csharp
public interface IRepository<T> where T : IAggregate
{
    Task<T?> GetByIdAsync(Guid id, ...);
    Task AddAsync(T aggregate, ...);
}

// 编译期阻止乱用
IRepository<Admin> repo;       // ✅
IRepository<string> repo;      // ❌ string 不是 IAggregate
```

### 问题三：领域事件为什么在 Aggregate 基类，不在 Entity 基类？

只有聚合根有资格发布领域事件。

```csharp
// ✅ Member 是聚合根 — 有 AddDomainEvent
public class Member : Aggregate<MemberId>
{
    public void Disable()
    {
        IsActive = false;
        AddDomainEvent(new MemberDisabledEvent(Id));  // ✅
    }
}

// ❌ 如果 PlatformSession 是普通 Entity — 没有 AddDomainEvent
// 它的改动应该由所属的 Member 聚合根统一管理
```

**聚合根是它管辖范围内所有实体的"总闸"。** 里面的子实体发生变动，聚合根判断是否需要对外广播。如果一个子实体自己就能发领域事件，那它就不再是"子实体"而是独立的聚合根了。

### Aggregate 基类的实现细节

```csharp
public abstract class Aggregate<TId> : Entity<TId>, IAggregate<TId>
{
    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyList<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    public void AddDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Add(domainEvent);   // 只收集，不立刻发布
    }

    public IDomainEvent[] ClearDomainEvents()
    {
        var events = _domainEvents.ToArray();
        _domainEvents.Clear();
        return events;
    }
}
```

关键设计：**收集事件 → 延迟发布**。

```
Member.Disable()      →  AddDomainEvent(...)     事件只进列表
Member.Extend(30)     →  AddDomainEvent(...)     再进一条
_repo.Update(member)  →  SaveChanges 前 → ClearDomainEvents() 取出所有事件
                         → MediatR 发布 → Handler 响应
                         → 数据库事务提交
```

如果 Handler 处理失败 → 数据库事务回滚 → 事件不丢、数据不改。**事件和持久化在同一个事务中。**

---

## 3. 为什么需要强类型 Id（AdminId / MemberId）

写 Java/写 C# 久了，习惯 `int Id`。但在 DDD 里推荐用强类型 Id，原因是：

```csharp
// ❌ 原始类型 — 两个 int，顺序搞反编译器不吭声
void ActivateCode(int codeId, int memberId) { }

ActivateCode(memberId, codeId);  // 编译通过，运行炸了

// ✅ 强类型 — 编译器拦截
void ActivateCode(ActivationCodeId codeId, MemberId memberId) { }

ActivateCode(memberId, codeId);  // ❌ 编译错误！
```

CreatFlow 所有强类型 Id 都跟一个模式写：

```csharp
public record AdminId
{
    public Guid Value { get; }

    private AdminId(Guid value) => Value = value;   // private 构造器

    public static AdminId Of(Guid value)             // 工厂方法
    {
        if (value == Guid.Empty)
            throw new DomainException("AdminId cannot be empty.");
        return new AdminId(value);
    }
}
```

`record` 的好处：值相等（相同 Guid → 相同 Id），不是引用相等。两个 `AdminId.Of(sameGuid)` 互相 `Equals`。

---

## 4. 为什么需要 Username / PasswordHash 值对象

### 问题：用裸 string 的后果

```csharp
// 原始写法 — 两个 string
public class Admin
{
    public string UserName { get; set; }    // 什么都能放
    public string PassWord { get; set; }    // 明文还是哈希？不知道
}

// 校验散落在各处
if (username.Length < 3) throw ...;  // Controller
if (username.Length < 3) throw ...;  // Service A
if (username.Length < 3) throw ...;  // Service B — 改规则时漏改这里

// 语义模糊
admin.Password = "myPassword";       // 这存的是明文？应该报错！
admin.Password = "$2a$11$K3...";     // 这是哈希，但类型上看不出来
```

### 值对象的解决方案

```csharp
// Username — 构造时校验，只写一次
public sealed record Username
{
    public string Value { get; }

    public Username(string value)
    {
        ArgumentNullException.ThrowIfNull(value);
        var trimmed = value.Trim();
        if (trimmed.Length < 3 || trimmed.Length > 50)
            throw new DomainException($"Username must be between 3 and 50 characters.");
        Value = trimmed.ToLowerInvariant();
    }
}

// PasswordHash — 类型名本身就是文档
public sealed record PasswordHash
{
    public string Hash { get; }

    public PasswordHash(string hash)
    {
        if (string.IsNullOrWhiteSpace(hash))
            throw new DomainException("Password hash cannot be empty.");
        Hash = hash;
    }
}
```

**值对象的特征**：

- 不可变（`sealed record`）— 改了就是新对象
- 相等性基于值 — `new Username("abc")` 等于另一个 `new Username("abc")`
- 自校验 — 不可能构造一个无效的 `Username`
- 语义明确 — `PasswordHash` 告诉所有人"这里面是哈希"

---

## 5. 领域事件（DomainEvent）

### 基本概念

聚合根修改状态时，会发出"发生了什么"的事件。其他组件可以订阅这些事件做响应。

```csharp
// 事件接口 — 纯类型标记
public interface IDomainEvent { }

// 具体事件 — record 天然适合
public record MemberDisabledEvent(MemberId MemberId) : IDomainEvent;
public record MemberActivatedEvent(MemberId MemberId, DateTime ExpireDate) : IDomainEvent;
public record MemberExtendedEvent(MemberId MemberId, DateTime NewExpireDate) : IDomainEvent;

// Member 内部发布事件
public void Disable()
{
    if (!IsActive) return;
    IsActive = false;
    AddDomainEvent(new MemberDisabledEvent(Id));
}
```

### 事件的用途（后续实现）

```
MemberDisabledEvent →
    → Redis 拉黑 token（该用户立刻不可用）
    → 审计日志写入
    → WebSocket 推送踢下线

这些 Handler 都是独立的，加新需求不用改 Member.cs。
```

### 为什么 IDomainEvent 不继承 MediatR 的 INotification

EShopMicroservices 那样写是因为微服务项目确定用 MediatR。CreatFlow 的 Domain 层保持**零外部依赖**——如果未来换消息库，只改 Infrastructure 层即可，Domain 层不用动。

---

## 6. 为什么 Admin 和 Member 分开设计

### 领域上的差异

| | Admin | Member |
|------|------|------|
| 谁用 | 你（管理员） | 付费用户 |
| 登录方式 | 浏览器 Blazor → Cookie | 桌面端 API → JWT |
| 会不会过期 | ❌ 永不过期 | ✅ 会员有期限 |
| 有没有禁用功能 | ❌ | ✅ `IsActive`/`Disable()` |
| 有没有续费功能 | ❌ | ✅ `Extend(days)` |
| 数量 | 1~3 个 | 成百上千 |

**如果放一张表**：

```sql
-- 反模式
CREATE TABLE users (
    role ENUM('admin', 'member'),
    expire_date DATETIME NULL,    -- admin 永远是 NULL
    is_active TINYINT(1) NULL,    -- admin 永远是 NULL
);
```

Admin 的 `expire_date`、`is_active` 永远是 NULL。查询会员时永远要带 `WHERE role = 'member'`。这是关系型数据库里经典的"一表多义"问题。

分开两张表 → 字段各管各的 → C# 类也各管各的 → 干净。

---

## 7. CreatFlow.Domain 完整文件清单

```text
src/CreatFlow.Domain/
├── Abstractions/
│   ├── IEntity.cs            ← 实体标记（IEntity 非泛型 + IEntity<T> 泛型）
│   ├── Entity.cs             ← 实体基类（Id + CreatedAt/LastModified）
│   ├── IAggregate.cs         ← 聚合根接口（DomainEvents + ClearDomainEvents）
│   ├── Aggregate.cs          ← 聚合根基类（事件收集列表 + Add/Clear 方法）
│   └── IDomainEvent.cs       ← 事件接口（空接口，不依赖 MediatR）
├── ValueObjects/
│   ├── AdminId.cs            ← record struct | Guid Value + Of() 工厂
│   ├── MemberId.cs           ← 同上
│   ├── Username.cs           ← sealed record | 3~50 字符 | trim+ToLower
│   └── PasswordHash.cs       ← sealed record | 存哈希字符串
├── Entities/
│   ├── Admin.cs              ← Aggregate<AdminId> | Create() + ChangePassword()
│   └── Member.cs             ← Aggregate<MemberId> | Create() + Disable() + Extend() + IsExpired()
├── Events/
│   ├── MemberActivatedEvent.cs   ← record(MemberId, ExpireDate)
│   ├── MemberDisabledEvent.cs    ← record(MemberId)
│   └── MemberExtendedEvent.cs    ← record(MemberId, NewExpireDate)
├── Shared/Interfaces/
│   └── IRepository.cs        ← 仓储接口（泛型约束 IAggregate）
├── Exceptions/
│   └── DomainException.cs    ← 领域异常
├── GlobalUsing.cs
└── CreatFlow.Domain.csproj   ← net10.0, 零 NuGet 包引用
```
