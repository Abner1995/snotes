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