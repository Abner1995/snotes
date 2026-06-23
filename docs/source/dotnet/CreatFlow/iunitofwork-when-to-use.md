# IUnitOfWork — 什么时候用

## 三种 SaveChanges 策略

### 方式 A — Repository 内部自己 Save（V1 推荐）

每个写操作立刻持久化。

```csharp
public async Task AddAsync(Member aggregate, CancellationToken ct)
{
    await _db.Members.AddAsync(aggregate, ct);
    await _db.SaveChangesAsync(ct);
}
```

| 优点 | 缺点 |
|------|------|
| 零学习成本，代码最简 | 多聚合操作不在同一个事务 |
| 单聚合场景完全够用 | — |

---

### 方式 B — Application 层直接调 DbContext（不推荐）

```csharp
// AuthService 注入 AppDbContext
await _memberRepo.AddAsync(member, ct);   // 不 Save
await _codeRepo.UpdateAsync(code, ct);    // 不 Save
await _db.SaveChangesAsync(ct);           // 一次性提交
```

| 优点 | 缺点 |
|------|------|
| 简单粗暴，一次提交 | Application 层依赖 EF Core，违反分层 |
| — | Infrastructure 细节泄漏到用例层 |

---

### 方式 C — IUnitOfWork（DDD 标准）

```csharp
// Application 层定义接口
public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}

// Infrastructure 实现
public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _db;
    public UnitOfWork(AppDbContext db) => _db = db;
    public Task<int> SaveChangesAsync(CancellationToken ct) => _db.SaveChangesAsync(ct);
}

// AuthService 使用
public class AuthService
{
    private readonly IMemberRepository _repo;
    private readonly IUnitOfWork _uow;

    public async Task<RegisterResult> RegisterAsync(RegisterCommand cmd, CancellationToken ct)
    {
        var member = Member.Create(...);
        await _repo.AddAsync(member, ct);     // 只跟踪，不 Save
        await _uow.SaveChangesAsync(ct);      // 一次提交
    }
}
```

| 优点 | 缺点 |
|------|------|
| 接口在 Application，实现在 Infrastructure，分层干净 | 多一个接口和一个类 |
| 多聚合操作在一个事务内 | 单聚合场景有点杀鸡用牛刀 |

---

## 什么时候需要 IUnitOfWork

**信号：一个用例操作了多个聚合根。**

```
不需要的场景（当前 CreatFlow V1）:
  LoginAsync       → 只读 IMemberRepository (查)
  RegisterAsync    → 只写 IMemberRepository (增)
  ChangePasswordAsync → 只写 IMemberRepository (改)

需要的场景:
  批量生成激活码    → IActivationCodeRepository (增多个 Code)
  激活码兑换会员    → IActivationCodeRepository (改) + IMemberRepository (增)
  管理员禁用用户    → IMemberRepository (改) + 记操作日志（另一个 Repo）
```

**判定规则：一个用例里，`SaveChangesAsync` 之前如果有 ≥2 个不同聚合的变更 → 就该引入 IUnitOfWork。**

---

## 迁移路径（从方式 A 到方式 C）

迁移成本很低，三步：

```
1. Application/Common/Interfaces/ 加 IUnitOfWork.cs
2. Infrastructure 加 UnitOfWork.cs 实现，DependencyInjection 注册
3. Repository 去掉内部的 SaveChangesAsync，AuthService 注入 IUnitOfWork
```

没有架构级改动，只是把 `SaveChangesAsync` 的调用位置从 Repository 内部上提到 Service。

---

## CreatFlow 的建议

| 阶段 | 策略 | 理由 |
|------|------|------|
| V1（当前） | 方式 A | 只有 Member 一个聚合，跨聚合事务为零 |
| V2（加了 ActivationCode） | 迁移到方式 C | 激活码兑换涉及两个聚合 |
| 以后 | 保持方式 C | 聚合越多，IUnitOfWork 价值越大 |
