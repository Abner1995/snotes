# Ordering.Domain

1. 实体接口和抽象类
IEntity<T> 和 IEntity 接口
```csharp
// 泛型实体接口，定义具有特定类型ID的实体
public interface IEntity<T> : IEntity
{
    public T Id { get; set; }  // 实体唯一标识
}

// 基础实体接口，定义审计字段
public interface IEntity
{
    public DateTime? CreatedAt { get; set; }      // 创建时间
    public string? CreatedBy { get; set; }        // 创建人
    public DateTime? LastModified { get; set; }   // 最后修改时间
    public string? LastModifiedBy { get; set; }   // 最后修改人
}
```  
作用：定义实体的基本契约，包含审计跟踪信息。

Entity<T> 抽象类
```csharp
public abstract class Entity<T> : IEntity<T>
{
    public T Id { get; set; }
    // 实现所有审计字段
}
```
作用：提供实体类的具体实现，所有领域实体都可以继承这个基类。

2. 领域事件接口
IDomainEvent 接口
```csharp
public interface IDomainEvent : INotification
{
    Guid EventId => Guid.NewGuid();                    // 事件唯一ID
    public DateTime OccurredOn => DateTime.Now;        // 事件发生时间
    public string EventType => GetType().AssemblyQualifiedName;  // 事件类型
}
```
作用：
- 定义领域事件的契约
- 继承 MediatR 的 INotification，支持中介者模式
- 提供事件的元数据（ID、时间、类型）

3. 聚合根接口
IAggregate<T> 和 IAggregate 接口
```csharp
public interface IAggregate<T> : IAggregate, IEntity<T>
{
}

public interface IAggregate : IEntity
{
    IReadOnlyList<IDomainEvent> DomainEvents { get; }  // 领域事件列表
    IDomainEvent[] ClearDomainEvents();                // 清空领域事件
}
```
作用：

- 定义聚合根的契约
- 管理领域事件的集合
- 确保聚合根也是实体（具有ID和审计字段）

4. 聚合根抽象类
Aggregate<TId> 类
```csharp
public abstract class Aggregate<TId> : Entity<TId>, IAggregate<TId>
{
    private readonly List<IDomainEvent> _domainEvents = new();
    
    public void AddDomainEvent(IDomainEvent domainEvent)
    {
        _domainEvents.Add(domainEvent);
    }

    public IDomainEvent[] ClearDomainEvents()
    {
        var events = _domainEvents.ToArray();
        _domainEvents.Clear();
        return events;
    }
}
```
作用：

- 提供聚合根的具体实现
- 管理领域事件的生命周期
- 在领域操作中收集事件，在持久化时清空并处理事件

5. 整体架构价值
- 关注点分离：清晰的分层架构
- 审计跟踪：自动记录实体变更历史
- 事件驱动：支持领域事件模式
- 一致性：确保聚合根内的业务规则一致性
- 可测试性：清晰的接口便于单元测试

这种设计模式在DDD项目中非常常见，提供了坚实的基础架构支持复杂的业务逻辑。