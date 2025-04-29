# MySQL  

```bash  
mysql -u root -p
```  

```bash  
# 查询所有的库
show databases;
# 进入数据库“student”是库名
use student;
# 查询所有的表
show tables;
```  

```bash  
# 查看正在执行的SQL语句
SHOW PROCESSLIST;
# 查询线程 ID 为 10 的连接信息
SELECT * FROM information_schema.PROCESSLIST WHERE ID = 336;
# 查找长时间Sleep连接
SELECT * FROM information_schema.processlist WHERE COMMAND = 'Sleep' AND db = 'kf_iqitz_com';
SELECT * FROM information_schema.processlist WHERE COMMAND = 'Sleep' AND db = 'kf_iqitz_com' AND host LIKE '117.80.57.65%';
SELECT * FROM information_schema.processlist WHERE COMMAND = 'Sleep' AND db = 'aichongchong_com';
SELECT * FROM information_schema.processlist WHERE COMMAND = 'Sleep' AND db = 'kf_iqitz_com' AND TIME > 60;

# 如果需要批量终止，可以使用以下脚本
SELECT CONCAT('KILL CONNECTION ', id, ';') FROM information_schema.processlist WHERE user = 'kf_iqitz_com' AND host LIKE '117.80.57.65%' AND command = 'Sleep';
```  

```bash  
# 查看慢查询是否开启
SHOW VARIABLES LIKE '%slow_query_log%';
# 开启慢查询
SET GLOBAL slow_query_log='ON';
# 查看慢查询日志位置
SHOW VARIABLES LIKE '%slow_query_log_file%';
# 查看慢查询阈值，单位：秒
SHOW GLOBAL VARIABLES LIKE '%long_query_time%';
# 修改慢查询阈值，单位：秒
SET long_query_time=1;
# 查看慢查询语句的数量
SHOW GLOBAL STATUS LIKE '%Slow_queries';
```  

```bash  
# 28800
SELECT @@global.wait_timeout, @@session.wait_timeout, @@session.interactive_timeout;
```  

```bash  
# 监控Sleep连接数
SHOW STATUS LIKE 'Threads_connected';
# 活跃连接数
SHOW STATUS LIKE 'Threads_running';
``` 

```bash  
# 监控 InnoDB 锁
SHOW ENGINE INNODB STATUS;
``` 

## 工具  

### Valgrind
```bash 
sudo -u mysql valgrind --tool=memcheck --leak-check=full --track-origins=yes --log-file=/tmp/valgrind.log /www/server/mysql/bin/mysqld --no-defaults --basedir=/www/server/mysql --datadir=/www/server/data
``` 

