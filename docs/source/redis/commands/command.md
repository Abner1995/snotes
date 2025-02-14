# 常用命令  

```shell  
# 使用密码连接Redis客户端
redis-cli -h [hostname] -p [port] -a yourpassword

# 查询Redis中所有key
keys *

# 查询Redis中所有某个key的值
get test

# 删除key
del test

# 查找所有以 "user" 开头的 keys
SCAN 0 MATCH *urlpath_city_count*
KEYS *urlpath_city_count*  

# 获取hash表数据  
HGETALL courier:1

# 查看list数据  
LRANGE aichongchong:front:city:riderquque 0 4  

LRANGE aichongchong:front:order:quque:7765 0 5000  

# 查看zset数据  
ZRANGE aichongchong:front:couriers:geo:896:0 0 10000 WITHSCORES
ZRANGE aichongchong:front:business:geo:896:0 0 10000 WITHSCORES

# 查看set数据  
SMEMBERS aichongchong:front:orderidsmessage  
# 删除set数据某个元素
SREM aichongchong:front:orderidsmessage 7767

keys * 

keys aichongchong:front:order*  

keys aichongchong:front:order:quque*  

keys aichongchong:front:couriers:geo:896*  
keys aichongchong:front:business:geo:896*

get aichongchong:front:businessinfo:896:61

LRANGE aichongchong:front:order:quque:7763 0 1000  

zAdd zRange
sAdd sMembers
rpush lpop
```  

# redis配置  

## RDB  
1. dir 设置指定了 RDB 文件所在的目录。
2. dbfilename 设置指定了 RDB 文件的名称。 
   
## 日志  
1. 在配置文件中找到 logfile 和 loglevel 设置。
2. 将 logfile 设置为一个有效的路径，例如 /var/log/redis/redis.log。
3. 将 loglevel 设置为 notice 或更高的级别，例如 debug。
