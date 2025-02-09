# 导航属性  

:::{note}  
可以在实体类中定义虚性属性，不会映射到数据库，但是可以指向另一个实体类，从而实现一对多、多对多、一对多、多对多等关系，可以在查询中使用   
可以在Fluent API配置，不会映射到数据库，不可以在查询中使用  
在数据库迁移builder.Ignore(c => c.Phones)必须添加这句话，不然无法迁移成功
:::  

## Contact实体类配置
```csharp  
namespace ContactSMS.Domain.Entity
{
    public class Contact
    {
        public long Id { get; set; }
        public string Name { get; set; }
        public string? Company { get; set; }
        // 声明虚拟导航属性，无需映射到数据表中，可以使用EFCore中的虚拟导航属性
        public virtual List<Phone>? Phones { get; set; }
    }
}
```  

## Contact实体类Fluent API配置  

```csharp  
using ContactSMS.Domain.Entity;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace ContactSMS.Infrastructure.Configs
{
    public class ContactConfig : IEntityTypeConfiguration<Contact>
    {
        public void Configure(EntityTypeBuilder<Contact> builder)
        {
            builder.ToTable($"T_{nameof(Contact)}".ToLower(), t => t.HasComment("联系人"));
            builder.HasKey(t => t.Id);
            builder.Property(t => t.Name).IsRequired().HasComment("姓名");
            builder.Property(t => t.Company).HasComment("公司");
            // 忽略导航属性，无需映射到数据表中，不可以使用EFCore中的虚拟导航属性
            builder.Ignore(c => c.Phones);
        }
    }
}
```  