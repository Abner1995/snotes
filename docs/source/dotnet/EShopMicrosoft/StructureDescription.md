# 项目结构  

## 核心基础设施  

|项目名称|作用
|-|-
|eShop.AppHost|Aspire 应用宿主，用于协调所有微服务和依赖项（如数据库、Redis）的本地开发环境。
|eShop.ServiceDefaults|包含微服务的默认配置（健康检查、OpenTelemetry、Dapr 集成等），供其他服务复用。

## 微服务模块  

|项目名称|作用
|-|-
|BasketAPI|购物车服务，管理用户购物车数据，通常与 Redis 集成实现高性能缓存。
|CatalogAPI|商品目录服务，提供商品查询、分类管理，使用 PostgreSQL 或 SQL Server 存储数据。
|IdentityAPI|身份认证服务，基于 ASP.NET Core Identity，处理用户登录、注册、JWT 令牌颁发。
|OrderingAPI|订单服务，处理订单创建、状态管理，依赖 OrderingDomain 和 Ordering.Infrastructure。
|Webhooks.API|Webhook 服务，允许外部系统订阅事件（如订单状态变更）。
|Mobile.Bff.Shopping|面向移动端的 BFF（Backend for Frontend），聚合多个微服务的数据。

## 前端与客户端 

|项目名称|作用
|-|-
|ClientApp|前端应用（可能是 Blazor WebAssembly 或 React/Vue），提供用户界面。
|WebApp|主 Web 应用（如 MVC 或 Razor Pages），可能包含管理后台。
|WebAppComponents|共享的 UI 组件库（如 Razor 类库）。
|HybridApp|混合移动应用（如 .NET MAUI），跨平台移动端实现。

## 事件总线与消息队列  

|项目名称|作用
|-|-
|EventBus|抽象事件总线接口，定义发布/订阅模式。
|EventBusRabbitMQ|RabbitMQ 的事件总线实现，用于服务间异步通信。
|IntegrationEventLogEF|集成事件日志（EF Core 实现），确保事件最终一致性。

## 订单处理相关  

|项目名称|作用
|-|-
|OrderingDomain|订单领域模型（DDD 设计），包含实体、值对象和领域逻辑。
|Ordering.Infrastructure|订单基础设施层（数据库访问、仓储实现）。
|OrderProcessor|后台服务，处理订单状态机或长时间运行流程。
|PaymentProcessor|支付处理服务，模拟或集成第三方支付网关。

## 其他工具类库

|项目名称|作用
|-|-
|WebhookClient|Webhook 客户端示例，演示如何调用 Webhooks.API。

## 测试项目（tests 目录）

|项目名称|作用
|-|-
|Basket.UnitTests|购物车服务的单元测试。
|Catalog.FunctionalTests|商品目录服务的功能测试（API 测试）。
|Ordering.UnitTests|订单领域模型的单元测试。
|Ordering.FunctionalTests|订单服务的功能测试。

## 关键架构特点
1. 模块化设计：每个功能（如购物车、订单）独立为微服务。
2. 事件驱动：通过 EventBus 实现服务解耦。
3. 前后端分离：ClientApp 和 WebApp 分别处理不同终端。
4. DDD 实践：OrderingDomain 体现领域驱动设计。