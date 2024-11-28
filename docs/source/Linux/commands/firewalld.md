# firewalld 
```bash  
# 添加  
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="150.138.245.0/24" drop'  
```  

```bash  
# 删除  
sudo firewall-cmd --permanent --remove-rich-rule='rule family="ipv4" source address="150.138.245.0/24" drop'  
```  

```bash  
# 重载  
sudo firewall-cmd --reload   
```  

```bash  
# 查看  
sudo firewall-cmd --list-all   
```  

> [!NOTE]
> 添加或删除之后需要重载才生效  
>
