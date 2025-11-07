# 线上调试  

## 网站防护

### 开始排查
```bash
# 查看当前访问最多的 IP
netstat -an | grep :80 | awk '{print $5}' | cut -d":" -f1 | sort | uniq -c | sort -nr | head -n 20
netstat -an | grep :443 | awk '{print $5}' | cut -d":" -f1 | sort | uniq -c | sort -nr | head -n 20
netstat -nt | awk '/:443/ {print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20
netstat -nt | awk '/:80/ {print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20
netstat -nt | grep :80 | wc -l
netstat -nt | grep :443 | wc -l

# 查看连接数最多的 IP
netstat -ntu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

# 查看 TCP 连接（SYN Flood、HTTP Flood 等）
netstat -nt | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

# 查看 UDP “连接”（实际是最近通信的对端）
netstat -nu | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -20

# 查看这些高连接IP的访问行为
grep "150.138.245" /www/wwwlogs/www.fangth.cn.log | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

# 查看User-Agent
grep "150.138.245" /www/wwwlogs/www.fangth.cn.log | awk -F'"' '{print $6}' | sort | uniq -c | sort -nr | head -10

# 查看这些攻击IP在访问什么内容
grep -E "150.138.245|111.63.71" /www/wwwlogs/www.fangth.cn.log | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

# 查看攻击的时间分布
grep "150.138.245.239" /www/wwwlogs/www.fangth.cn.log | awk '{print $4}' | cut -d: -f1,2 | sort | uniq -c | head -10
```

### iptables
```bash
# 查看现有规则及编号
iptables -L INPUT --line-numbers

# 根据编号删除规则
iptables -D INPUT 1

# 通过精确匹配规则本身来删除它
iptables -D INPUT -s 150.138.245.0/24 -j DROP
iptables -D INPUT -s 111.63.71.0/24 -j DROP

# 保存 iptables 配置
service iptables save
# 或者
netfilter-persistent save
# 或者
/etc/init.d/iptables-persistent save
```

```bash
# 1. 封禁IP段
iptables -I INPUT -s 150.138.245.0/24 -j DROP
iptables -I INPUT -s 111.63.71.0/24 -j DROP

# 2. 重载nginx配置
nginx -t && nginx -s reload

# 3. 监控效果
netstat -nt | grep :443 | grep ESTABLISHED | wc -l

# 4. 影响到了正常用户，通过精确匹配规则本身来删除它
iptables -D INPUT -s 150.138.245.0/24 -j DROP
iptables -D INPUT -s 111.63.71.0/24 -j DROP
```

## 打印系统信息
```bash
uname -m
arch
#CPU 的详细信息，其中包括架构信息。
cat /proc/cpuinfo
``` 

## 找出占用内存高的进程
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



```bash
strace -p pid -
``` 

```bash

# 检查连接状态，确认是否是正常 Established 连接
netstat -nt | grep :443 | grep ESTABLISHED | wc -l  
# 查看所有ESTABLISHED连接的完整分布
netstat -nt | grep :443 | grep ESTABLISHED | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -30
# 每2秒刷新连接数
watch -n 2 "netstat -nt | grep :443 | grep ESTABLISHED | wc -l"

# 监控前10名IP的变化
watch -n 5 "netstat -nt | grep :443 | grep ESTABLISHED | awk '{print \$5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head -10"

# 查看所有TCP连接的状态分布
netstat -nt | awk '/^tcp/ {++S[$NF]} END {for(a in S) print a, S[a]}'

# Nginx状态
nginx -t && echo "Nginx配置正常"

# 查看当前QPS（每秒请求数）
tail -f /www/wwwlogs/access.log | pv -l > /dev/null



``` 

# 使用 iptables 封禁（示例）
```bash
iptables -A INPUT -s 1.2.3.4 -j DROP

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

# nginx

```bash
# 查看 nginx 配置文件
/www/server/nginx/conf/nginx.conf  

``` 

atop -r /var/log/atop/atop_20251106 -b 15:00

# 1. 检查MySQL在16:20左右的慢查询
sudo grep "16:2[0-9]" /www/server/data/mysql-slow.log

# 2. 查看MySQL二进制日志时间点
sudo mysqlbinlog /var/lib/mysql/binlog.xxxxxx | grep "16:20"

# 3. 检查是否有定时任务在16:20执行
sudo crontab -l
sudo grep -r "16:20" /etc/cron.*