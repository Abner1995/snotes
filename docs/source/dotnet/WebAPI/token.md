# 生成token

## 包安装

```bash
Microsoft.AspNetCore.Authentication.JwtBearer  
Microsoft.IdentityModel.Tokens  
System.IdentityModel.Tokens.Jwt  
```

1. <mark style="color:red;">**先创建下面几个文件**</mark>
   1. PolicyContstants用于JWT的Policy常量
   2. AuthenticationData用于用户登录
   3. UserData用于用户登录后存储信息

```csharp
namespace ContactSMS.WebAPI.Constants
{
    public static class PolicyContstants
    {
        public const string MustHaveEmployeeId = "MustHaveEmployeeId";
        public const string MustBeTheOwner = "MustBeTheOwner";
    }
}
```

```csharp
public record AuthenticationData(string? UserName, string Password);
```

```csharp
public record UserData(long UserId, string UserName, string Title, string EmployeeId);
```

2. <mark style="color:red;">**新建AuthenticationController控制器**</mark>
   1. 这里只是示例，没有和数据交互

<pre class="language-csharp"><code class="lang-csharp">namespace ContactSMS.WebAPI.Controllers;

[Route("api/[controller]")]
[ApiController]
public class AuthenticationController : ControllerBase
{
    private readonly IConfiguration _configuration;

    public record AuthenticationData(string? UserName, string Password);
    public record UserData(long UserId, string UserName, string Title, string EmployeeId);

    public AuthenticationController(IConfiguration configuration)
    {
        this._configuration = configuration;
    }

    //[HttpPost("token")]: 指定这是一个处理 HTTP POST 请求的方法，路径为 api/authentication/token。
    //[AllowAnonymous]: 该属性允许未经身份验证的请求访问此方法。
    //请求体绑定: 使用 [FromBody] 绑定请求体中的数据到 AuthenticationData 类型的对象。
    //调用 ValidateCredentials 方法: 验证用户的凭据。
    //生成令牌: 如果验证成功，调用 GenerateToken 方法生成 JWT 令牌。
    //返回结果: 返回一个包含 JWT 令牌的 Ok 响应。如果验证失败，则调用 Unauthorized() 方法返回未授权状态。
    [HttpPost("token")]
    [AllowAnonymous]
    public ActionResult&#x3C;string> Authentication([FromBody] AuthenticationData data)
    {
        var user = ValidateCredentials(data);
        if (user is null)
        {
            Unauthorized();
        }
        var token = GenerateToken(user!);
        return Ok(token);
    }

<strong>    //创建密钥: 使用从配置文件中读取的密钥创建一个对称密钥。
</strong>    //创建签名凭证: 创建一个签名凭证，用于生成 JWT 令牌。
    //创建声明列表: 为 JWT 令牌添加声明（claims），包括用户 ID、用户名、标题和员工 ID。
    //创建 JWT 令牌: 使用 JwtSecurityToken 类创建一个 JWT 令牌，指定发行人（issuer）、受众（audience）、声明列表、有效期和签名凭证。
    //序列化令牌: 使用 JwtSecurityTokenHandler 类将 JwtSecurityToken 序列化为字符串。
    private string GenerateToken(UserData user)
    {
        var secretKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(
                this._configuration.GetSection("Authentication:SecretKey").Value!));

        var signingCredentials = new SigningCredentials(secretKey, SecurityAlgorithms.HmacSha512Signature);

        List&#x3C;Claim> claims = new();
        claims.Add(new(JwtRegisteredClaimNames.Sub, user.UserId.ToString()));
        claims.Add(new(JwtRegisteredClaimNames.UniqueName, user.UserName));
        claims.Add(new("title", user.Title));
        claims.Add(new("employeeId", user.EmployeeId));

        var token = new JwtSecurityToken(
            this._configuration.GetSection("Authentication:Issuer").Value!,
            this._configuration.GetSection("Authentication:Audience").Value!,
            claims,
            DateTime.UtcNow,
            DateTime.UtcNow.AddMinutes(1),
            signingCredentials);
        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private UserData? ValidateCredentials(AuthenticationData data)
    {
        //示例
        if (CompareValues(data.UserName, "xuzizheng") &#x26;&#x26;
            CompareValues(data.Password, "123456"))
        {
            return new UserData(1, data.UserName!, "Business owner", "E001");
        }
        if (CompareValues(data.UserName, "zizheng") &#x26;&#x26;
            CompareValues(data.Password, "123456"))
        {
            return new UserData(1, data.UserName!, "rider owner", "E002");
        }
        return null;
    }

    private bool CompareValues(string? actual, string expected)
    {
        if (actual is not null)
        {
            if (actual.Equals(expected, StringComparison.InvariantCultureIgnoreCase))
            {
                return true;
            }
        }
        return false;
    }
}
</code></pre>

3. <mark style="color:red;">**Program.cs配置JWT相关**</mark>

```csharp
builder.Services.AddAuthorization(options =>
{
    // 定义一个授权策略，名为 MustHaveEmployeeId
    options.AddPolicy(PolicyContstants.MustHaveEmployeeId, policy =>
    {
        // 该策略要求用户必须有一个名为 "employeeId" 的声明（claim）
        policy.RequireClaim("employeeId");
    });

    // 定义另一个授权策略，名为 MustBeTheOwner
    options.AddPolicy(PolicyContstants.MustBeTheOwner, policy =>
    {
        // 该策略要求用户必须有一个名为 "title" 的声明，并且该声明的值必须是 "Business owner"
        policy.RequireClaim("title", "Business owner");
    });

    // 设置一个全局的回退策略
    // 如果没有特定的策略被应用，那么将使用这个默认策略
    // 这个策略要求用户必须通过身份验证（即必须是经过身份验证的用户）
    options.FallbackPolicy = new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build();
});

```

#### 各部分详细说明

1. **`builder.Services.AddAuthorization(options => { ... });`**:
   * 这是向依赖注入容器中添加授权配置的入口。它提供一个 `options` 参数来定义授权策略。
2. **`options.AddPolicy(PolicyContstants.MustHaveEmployeeId, policy => { ... });`**:
   * 这里定义了一个名为 `MustHaveEmployeeId` 的自定义授权策略。
   * 这个策略要求用户必须有一个声明（Claim），声明的键为 `"employeeId"`。如果用户没有这个声明，就无法通过授权。
3. **`options.AddPolicy(PolicyContstants.MustBeTheOwner, policy => { ... });`**:
   * 这里定义了另一个名为 `MustBeTheOwner` 的自定义授权策略。
   * 这个策略要求用户必须有一个 `"title"` 声明，并且这个声明的值必须是 `"Business owner"`。只有满足这个条件的用户才能通过授权。
4. **`options.FallbackPolicy = new AuthorizationPolicyBuilder().RequireAuthenticatedUser().Build();`**:
   * 这是一个全局的回退策略，称为 Fallback Policy。
   * 如果没有在特定路由或控制器上明确应用授权策略，ASP.NET Core 将使用这个回退策略。
   * 这个回退策略要求用户必须是经过身份验证的（即，用户必须登录）。如果用户未认证，他们将无法访问。

主要用途

* **自定义授权策略**：通过 `AddPolicy` 方法，开发者可以定义复杂的访问控制规则，例如要求用户拥有某些特定的声明（claims）或者角色。
* **回退策略**：通过设置 `FallbackPolicy`，可以确保所有未明确指定策略的请求都要求用户身份验证。

```csharp
builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new()
        {
            // 是否验证令牌的签发者
            ValidateIssuer = true,

            // 是否验证令牌的接收者（受众）
            ValidateAudience = true,

            // 是否验证签名密钥
            ValidateIssuerSigningKey = true,

            // 期望的签发者 (Issuer)
            ValidIssuer = builder.Configuration.GetSection("Authentication:Issuer").Value,

            // 期望的受众 (Audience)
            ValidAudience = builder.Configuration.GetSection("Authentication:Audience").Value,

            // 用于验证签名密钥的 SymmetricSecurityKey
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration.GetSection("Authentication:SecretKey").Value!))
        };
    });

```

#### 各部分详细说明

1. **`builder.Services.AddAuthentication("Bearer")`**:
   * 这是添加身份验证服务的入口，参数 `"Bearer"` 表示使用 Bearer Token 作为认证方案。Bearer Token 是 HTTP 认证的一种方式，通常用于 JWT。
   * 这里指明 ASP.NET Core 应用程序将在请求中查找 Bearer Token 来认证用户。
2. **`AddJwtBearer(options => { ... })`**:
   * 这个方法为应用程序配置 JWT Bearer Token 身份验证。
   * `options` 是配置 JWT 验证的参数。
3. **`TokenValidationParameters`**:
   * 这是 JWT 验证时使用的参数配置，用于指定验证规则。以下是各个参数的作用：
   * **`ValidateIssuer = true`**:
     * 该项表示是否要验证 JWT 令牌的签发者（Issuer）。签发者是指生成令牌的服务器。
     * 在验证过程中，令牌的签发者必须与配置中的 `ValidIssuer` 相匹配。
   * **`ValidateAudience = true`**:
     * 该项表示是否要验证令牌的接收者（受众，Audience）。受众是指谁可以接收和使用该令牌。
     * 在验证过程中，令牌的受众必须与配置中的 `ValidAudience` 相匹配。
   * **`ValidateIssuerSigningKey = true`**:
     * 该项表示是否要验证签名密钥，确保令牌是由合法方签署的，并且没有被篡改。
     * 签名密钥使用 `IssuerSigningKey` 参数进行验证。
4. **`ValidIssuer`**:
   * 期望的 JWT 令牌签发者。它从应用程序的配置文件（例如 `appsettings.json`）中获取 `"Authentication:Issuer"` 的值。
   * 这是生成令牌的服务器的标识，令牌的 `iss` 字段必须与此值匹配。
5. **`ValidAudience`**:
   * 期望的 JWT 令牌受众，指定哪些客户端可以使用该令牌。它从配置文件中获取 `"Authentication:Audience"` 的值。
   * 令牌的 `aud` 字段必须与此值匹配。
6.  **`IssuerSigningKey`**:

    * 用于验证 JWT 令牌签名的密钥。这里使用对称加密算法，通过 `SymmetricSecurityKey` 和 `SecretKey` 生成。
    * `SecretKey` 是一个用于生成签名密钥的字符串，它通常存储在配置文件中。

    ```csharp
    IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(builder.Configuration.GetSection("Authentication:SecretKey").Value!))
    ```

    这行代码从配置中读取 `"Authentication:SecretKey"`，并将其转化为字节数组来构建加密密钥。这个密钥用于签名和验证 JWT。

#### 主要用途

1. **身份验证**：这段代码配置了 JWT 令牌验证规则，用于验证客户端请求中的 JWT 令牌是否合法。
2. **安全性**：通过验证 Issuer、Audience 和签名密钥，确保 JWT 令牌的完整性，防止令牌被伪造或篡改。
3. **Bearer Token 认证方案**：整个配置为 API 提供了基于 JWT 的 Bearer Token 身份验证，常用于无状态的 Web 应用程序中。



4. <mark style="color:red;">**新建UserController控制器如何使用JWT特性**</mark>

```csharp
namespace ContactSMS.WebAPI.Controllers;

[Route("api/[controller]")]
[ApiController]
public class UserController : ControllerBase
{
    //[Authorize(Policy = PolicyContstants.MustHaveEmployeeId)]
    //这个属性用于授权访问，确保用户必须拥有特定的 employeeId 声明（Claim）。只有具有这个声明的用户才被允许访问此 API。
    //这里使用了自定义的授权策略 PolicyContstants.MustHaveEmployeeId，这个策略在应用程序中定义，要求 employeeId 声明。
    //[Authorize(Policy = PolicyContstants.MustBeTheOwner)]
    //这也是一个授权属性，确保用户必须拥有一个特定的 title 声明（比如，用户的职位是“Business owner”）。这里使用了另一个自定义的授权策略 PolicyContstants.MustBeTheOwner。
    //用户只有同时具备这两个策略的要求才能访问这个方法。
    [HttpGet("{id}")]
    [Authorize(Policy = PolicyContstants.MustHaveEmployeeId)]
    [Authorize(Policy = PolicyContstants.MustBeTheOwner)]
    public string Get(int id)
    {
        return id;
    }
}

```

