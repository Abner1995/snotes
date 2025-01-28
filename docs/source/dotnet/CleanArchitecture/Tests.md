# Tests  

Visual Studio插件 xUnit.net.TestGenerator2022  

```bash  
Install-Package FluentAssertions
```  

创建CleanArchitecture.ApplicationTests单元测试 
CurrentUserTests.cs
```csharp  
using CleanArchitecture.Domain.Constants;
using Xunit;
using FluentAssertions;

namespace CleanArchitecture.Application.Users.Tests;

public class CurrentUserTests
{
    [Theory()]
    [InlineData(UserRoles.Admin)]
    [InlineData(UserRoles.User)]
    public void IsInRole_WithMatchingRole_ShouldReturnTrue(string roleName)
    {
        var currentUser = new CurrentUser("1", "test@test.com", [UserRoles.Admin, UserRoles.User], null, null);
        var isInRole = currentUser.IsInRole(roleName);
        isInRole.Should().BeTrue();
    }


    [Fact()]
    public void IsInRole_WithNoMatchingRole_ShouldReturnFalse()
    {
        var currentUser = new CurrentUser("1", "test@test.com", [UserRoles.Admin, UserRoles.User], null, null);
        var isInRole = currentUser.IsInRole(UserRoles.Owner);
        isInRole.Should().BeFalse();
    }

    [Fact()]
    public void IsInRole_WithNoMatchingRoleCase_ShouldReturnFalse()
    {
        var currentUser = new CurrentUser("1", "test@test.com", [UserRoles.Admin, UserRoles.User], null, null);
        var isInRole = currentUser.IsInRole(UserRoles.Admin.ToLower());
        isInRole.Should().BeFalse();
    }
}
```  

UserContextTests.cs需要Mock  
```bash  
Install-Package Moq -Version 4.20.72
```  
```csharp 
using CleanArchitecture.Domain.Constants;
using FluentAssertions;
using Microsoft.AspNetCore.Http;
using Moq;
using System.Security.Claims;
using Xunit;

namespace CleanArchitecture.Application.Users.Tests;

public class UserContextTests
{
    [Fact()]
    public void GetCurrentUser_WithAuthenticatedUser_ShouldReturnCurrentUser()
    {
        var dateOfBirth = new DateOnly(1990, 1, 1);
        var httpContextAccessorMock = new Mock<IHttpContextAccessor>();
        var claims = new List<Claim>()
            {
                new(ClaimTypes.NameIdentifier, "1"),
                new(ClaimTypes.Email, "test@test.com"),
                new(ClaimTypes.Role, UserRoles.Admin),
                new(ClaimTypes.Role, UserRoles.User),
                new("Nationality", "German"),
                new("DateOfBirth", dateOfBirth.ToString("yyyy-MM-dd"))
            };

        var user = new ClaimsPrincipal(new ClaimsIdentity(claims, "Test"));

        httpContextAccessorMock.Setup(x => x.HttpContext).Returns(new DefaultHttpContext()
        {
            User = user
        });

        var userContext = new UserContext(httpContextAccessorMock.Object);
        var currentUser = userContext.GetCurrentUser();
        currentUser.Should().NotBeNull();
        currentUser.Id.Should().Be("1");
        currentUser.Email.Should().Be("test@test.com");
        currentUser.Roles.Should().ContainInOrder(UserRoles.Admin, UserRoles.User);
        currentUser.Nationality.Should().Be("German");
        currentUser.DateOfBirth.Should().Be(dateOfBirth);


    }

    [Fact]
    public void GetCurrentUser_WithUserContextNotPresent_ThrowsInvalidOperationException()
    {
        var httpContextAccessorMock = new Mock<IHttpContextAccessor>();
        httpContextAccessorMock.Setup(x => x.HttpContext).Returns((HttpContext)null);
        var userContext = new UserContext(httpContextAccessorMock.Object);
        Action action = () => userContext.GetCurrentUser();
        action.Should()
            .Throw<InvalidOperationException>()
            .WithMessage("User context is not present");
    }
}
```  


CleanArchitecture.Infrastructure  
```csharp 
using System.Runtime.CompilerServices;

[assembly: InternalsVisibleTo("CleanArchitecture.InfrastructureTests")]
```  

InternalsVisibleTo 特性指定了允许访问当前程序集内部成员（如 internal 修饰符的类、方法、属性等）的另一个程序集。这个特性使得在开发过程中，可以对程序集的内部成员进行单元测试，特别是在测试用例中需要访问 internal 成员时。

"CleanArchitecture.Infrastructure.Tests" 是一个指定的程序集名称，通常是指你写的单元测试项目的程序集。在这个例子中，CleanArchitecture.Infrastructure.Tests 是一个测试项目，可能用来测试 CleanArchitecture.Infrastructure 项目的功能。

CleanArchitecture.API.Tests如何添加CleanArchitecture.API的Program.cs  
在Program.cs文件中底部添加以下代码  
```csharp 
public partial class Program { }
```  