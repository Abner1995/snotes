# OpenApi.Extensions

这段代码是 eShop.ServiceDefaults 项目中关于 OpenAPI (Swagger) 集成的扩展方法，提供了标准化配置和版本管理功能。

## 主要功能概述
1. OpenAPI 文档生成：自动为 API 生成 Swagger/OpenAPI 文档
2. API 版本管理：支持多版本 API 文档
3. 开发工具集成：在开发环境提供 Scalar API 参考界面
4. 安全配置：集成认证授权信息到 OpenAPI 文档

## 方法详细解析

1. UseDefaultOpenApi 方法
    ```csharp
    public static IApplicationBuilder UseDefaultOpenApi(this WebApplication app)
    ```
    ### 功能：
    配置应用程序的 OpenAPI 中间件和开发工具。

    ### 关键逻辑：
    1. 检查配置中是否存在 OpenApi 部分
    2. 映射 OpenAPI 端点
    3. 在开发环境下：
        - 添加 Scalar API 参考界面
        - 重定向根路径到 Scalar 界面

    ### 使用场景：
    ```csharp
    var app = builder.Build();
    app.UseDefaultOpenApi();
    ```

2. AddDefaultOpenApi 方法
    ```csharp
    public static IHostApplicationBuilder AddDefaultOpenApi(
        this IHostApplicationBuilder builder,
        IApiVersioningBuilder? apiVersioning = default)
    ```
    ### 功能：
    配置 OpenAPI 文档生成和 API 版本管理。

    ### 关键逻辑：
    1. 从配置中获取 OpenAPI 和 Identity 相关设置
    2. 如果配置了 API 版本：
        - 设置版本格式（如 "v1"）
        - 为每个 API 版本配置 OpenAPI 文档
        - 应用各种文档转换器：
            - 标题和描述
            - 授权检查
            - 安全方案定义
            - 过时操作标记
            - 版本描述
            - 非空 schema
            - 清除默认服务器配置
    ### 参数：
    - apiVersioning: 可选的 API 版本配置构建器

    ### 使用场景：
    ```csharp
    var builder = WebApplication.CreateBuilder(args);
    builder.AddDefaultOpenApi();
    ```

    ### 核心设计特点
    1. 配置驱动：所有行为都基于 OpenApi 配置节
    2. 环境感知：开发环境特有功能（如 Scalar）
    3. 版本支持：完善的多版本 API 文档管理
    4. 安全集成：自动将认证方案加入文档

    ### 典型配置示例
    appsettings.json:
    ```json
    {
        "OpenApi": {
            "Document": {
            "Title": "eShop API",
            "Description": "eShop Microservices API"
            }
        },
        "Identity": {
            "Scopes": {
            "catalog": "Catalog API",
            "basket": "Basket API"
            }
        }
    }
    ```

## 集成工作流程
1. 服务注册阶段：
```csharp
builder.AddDefaultOpenApi();
```
2. 中间件管道构建阶段：
```csharp
app.UseDefaultOpenApi();
```
3. 运行时：
    - 访问 /openapi/v1.json 获取 v1 API 文档
    - 开发环境访问 /scalar 获得交互式文档

### 注意事项
1. 需要安装相关 NuGet 包：
    - Asp.Versioning
    - Scalar.AspNetCore
    - OpenAPI 相关包
2. 在非开发环境，Scalar 界面不会启用
3. API 版本管理是可选的，不传 apiVersioning 参数则不会启用版本功能

这段代码为 eShop 微服务提供了标准化的 API 文档解决方案，简化了各服务的 OpenAPI 配置工作。