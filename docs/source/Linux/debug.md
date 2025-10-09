# 线上调试  

打印系统信息
```bash
uname -m
arch
#CPU 的详细信息，其中包括架构信息。
cat /proc/cpuinfo
``` 

找出占用内存高的进程
```bash
ps aux --sort=-%mem | head -10
```  

查看 /proc/<pid>/stack 获取当前调用栈
```bash
sudo cat /proc/58515/stack
```  

用 netstat 查看连接数
```bash
netstat -antp | grep :80 | wc -l
``` 

# 查看当前访问最多的 IP
```bash
netstat -an | grep :80 | awk '{print $5}' | cut -d":" -f1 | sort | uniq -c | sort -nr | head -n 20
``` 

```bash
strace -p pid -
``` 

```bash
# 查看连接数最多的 IP
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

# 查看 TCP 连接（SYN Flood、HTTP Flood 等）
netstat -nt | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

# 查看 UDP “连接”（实际是最近通信的对端）
netstat -nu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20
``` 

# 使用 iptables 封禁（示例）
```bash
iptables -A INPUT -s 1.2.3.4 -j DROP

netstat -nt | awk '/:443/ {print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20
netstat -nt | awk '/:80/ {print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

netstat -nt | grep :80 | wc -l
netstat -nt | grep :443 | wc -l
``` 

# 清空现有规则（谨慎！确保你有其他访问方式如控制台）
```bash
iptables -F
``` 

```bash
# 封禁主要攻击网段
iptables -A INPUT -s 150.138.245.0/24 -j DROP
iptables -A INPUT -s 111.63.71.0/24 -j DROP
iptables -A INPUT -s 119.188.178.0/23 -j DROP  # 覆盖 178.x 和 179.x
``` 

```bash
# 可选：限制单 IP 最大连接数（防御漏网之鱼）
iptables -A INPUT -p tcp --syn --dport 80 -m connlimit --connlimit-above 30 -j REJECT --reject-with tcp-reset
iptables -A INPUT -p tcp --syn --dport 443 -m connlimit --connlimit-above 30 -j REJECT --reject-with tcp-reset

# 删除 80 端口规则
iptables -D INPUT -p tcp --syn --dport 80 -m connlimit --connlimit-above 30 -j REJECT --reject-with tcp-reset
# 删除 443 端口规则
iptables -D INPUT -p tcp --syn --dport 443 -m connlimit --connlimit-above 30 -j REJECT --reject-with tcp-reset
``` 