# MySQL  

## 进入命令行  
```shell  
mysql -u root -p  

# 查询所有的库
show databases; 

# 进入数据库“student”是库名
use student;

# 查询所有的表
show tables;

# 查看正在执行的SQL语句
SHOW PROCESSLIST;

# 查看慢查询是否开启
SHOW VARIABLES LIKE '%slow_query_log%'

# 开启慢查询
SET GLOBAL slow_query_log='ON'

# 查看慢查询日志位置
SHOW VARIABLES LIKE '%slow_query_log_file%'

# 查看慢查询阈值，单位：秒
SHOW GLOBAL VARIABLES LIKE '%long_query_time%'

# 修改慢查询阈值，单位：秒
SET long_query_time=1

# 查看慢查询语句的数量
SHOW GLOBAL STATUS LIKE '%Slow_queries'

# 测试执行一个慢查询语句
SELECT SLEEP(3);

# 我们想要按照查询时间排序，查看前五条 SQL 语句，这样写即可：
mysqldumpslow -s t -t 5 /www/server/data/mysql-slow.log

``` 
