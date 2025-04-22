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

strace -p pid -