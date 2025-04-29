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

KILL CONNECTION 104;                
KILL CONNECTION 105;                
KILL CONNECTION 202;                
KILL CONNECTION 99;                 
KILL CONNECTION 106;                
KILL CONNECTION 203;                
KILL CONNECTION 329;                
KILL CONNECTION 98;                 
KILL CONNECTION 107;                
KILL CONNECTION 204;                
KILL CONNECTION 330;                
KILL CONNECTION 88;                 
KILL CONNECTION 108;                
KILL CONNECTION 205;                
KILL CONNECTION 369;                
KILL CONNECTION 87;                 
KILL CONNECTION 109;                
KILL CONNECTION 206;                
KILL CONNECTION 83;                 
KILL CONNECTION 119;                
KILL CONNECTION 207;                
KILL CONNECTION 363;                
KILL CONNECTION 91;                 
KILL CONNECTION 112;                
KILL CONNECTION 208;                
KILL CONNECTION 365;                
KILL CONNECTION 76;                 
KILL CONNECTION 120;                
KILL CONNECTION 209;                
KILL CONNECTION 346;                
KILL CONNECTION 75;                 
KILL CONNECTION 121;                
KILL CONNECTION 210;                
KILL CONNECTION 364;                
KILL CONNECTION 85;                 
KILL CONNECTION 122;                
KILL CONNECTION 211;                
KILL CONNECTION 386;                
KILL CONNECTION 73;                 
KILL CONNECTION 123;                
KILL CONNECTION 212;                
KILL CONNECTION 380;                
KILL CONNECTION 72;                 
KILL CONNECTION 124;                
KILL CONNECTION 221;                
KILL CONNECTION 382;                
KILL CONNECTION 71;                 
KILL CONNECTION 125;                
KILL CONNECTION 214;                
KILL CONNECTION 387;                
KILL CONNECTION 70;                 
KILL CONNECTION 127;                
KILL CONNECTION 215;                
KILL CONNECTION 388;                
KILL CONNECTION 68;                 
KILL CONNECTION 128;                
KILL CONNECTION 389;                
KILL CONNECTION 66;                 
KILL CONNECTION 129;                
KILL CONNECTION 218;                
KILL CONNECTION 394;                
KILL CONNECTION 69;                 
KILL CONNECTION 130;                
KILL CONNECTION 222;                
KILL CONNECTION 392;                
KILL CONNECTION 63;                 
KILL CONNECTION 131;                
KILL CONNECTION 226;                
KILL CONNECTION 395;                
KILL CONNECTION 62;                 
KILL CONNECTION 227;                
KILL CONNECTION 137;                
KILL CONNECTION 396;                
KILL CONNECTION 61;                 
KILL CONNECTION 135;                
KILL CONNECTION 228;                
KILL CONNECTION 399;                
KILL CONNECTION 58;                 
KILL CONNECTION 136;                
KILL CONNECTION 400;                
KILL CONNECTION 57;                 
KILL CONNECTION 138;                
KILL CONNECTION 230;                
KILL CONNECTION 401;                
KILL CONNECTION 139;                
KILL CONNECTION 231;                
KILL CONNECTION 48;                 
KILL CONNECTION 140;                
KILL CONNECTION 232;                
KILL CONNECTION 426;                
KILL CONNECTION 143;                
KILL CONNECTION 233;                
KILL CONNECTION 422;                
KILL CONNECTION 45;                 
KILL CONNECTION 419;                
KILL CONNECTION 234;                
KILL CONNECTION 145;                
KILL CONNECTION 235;                
KILL CONNECTION 418;                
KILL CONNECTION 146;                
KILL CONNECTION 236;                
KILL CONNECTION 427;                
KILL CONNECTION 25;                 
KILL CONNECTION 147;                
KILL CONNECTION 237;                
KILL CONNECTION 428;                
KILL CONNECTION 26;                 
KILL CONNECTION 238;                
KILL CONNECTION 429;                
KILL CONNECTION 21;                 
KILL CONNECTION 152;                
KILL CONNECTION 239;                
KILL CONNECTION 430;                
KILL CONNECTION 16;                 
KILL CONNECTION 431;                
KILL CONNECTION 156;                
KILL CONNECTION 240;                
KILL CONNECTION 18;                 
KILL CONNECTION 241;                
KILL CONNECTION 161;                
KILL CONNECTION 432;                
KILL CONNECTION 17;                 
KILL CONNECTION 242;                
KILL CONNECTION 433;                
KILL CONNECTION 155;                
KILL CONNECTION 4;                  
KILL CONNECTION 159;                
KILL CONNECTION 243;                
KILL CONNECTION 434;                
KILL CONNECTION 2;                  
KILL CONNECTION 162;                
KILL CONNECTION 244;                
KILL CONNECTION 435;                
KILL CONNECTION 164;                
KILL CONNECTION 436;                
KILL CONNECTION 245;                
KILL CONNECTION 168;                
KILL CONNECTION 246;                
KILL CONNECTION 437;                
KILL CONNECTION 167;                
KILL CONNECTION 247;                
KILL CONNECTION 438;                
KILL CONNECTION 169;                
KILL CONNECTION 248;                
KILL CONNECTION 459;                
KILL CONNECTION 170;                
KILL CONNECTION 249;                
KILL CONNECTION 456;                
KILL CONNECTION 171;                
KILL CONNECTION 250;                
KILL CONNECTION 453;                
KILL CONNECTION 172;                
KILL CONNECTION 251;                
KILL CONNECTION 477;                
KILL CONNECTION 177;                
KILL CONNECTION 252;                
KILL CONNECTION 174;                
KILL CONNECTION 254;                
KILL CONNECTION 176;                
KILL CONNECTION 255;                
KILL CONNECTION 484;                
KILL CONNECTION 178;                
KILL CONNECTION 256;                
KILL CONNECTION 532;                
KILL CONNECTION 179;                
KILL CONNECTION 257;                
KILL CONNECTION 525;                
KILL CONNECTION 180;                
KILL CONNECTION 270;                
KILL CONNECTION 181;                
KILL CONNECTION 272;                
KILL CONNECTION 184;                
KILL CONNECTION 293;                
KILL CONNECTION 183;                
KILL CONNECTION 274;                
KILL CONNECTION 185;                
KILL CONNECTION 276;                
KILL CONNECTION 182;                
KILL CONNECTION 267;                
KILL CONNECTION 3265;               
KILL CONNECTION 188;                
KILL CONNECTION 292;                
KILL CONNECTION 189;                
KILL CONNECTION 291;                
KILL CONNECTION 192;                
KILL CONNECTION 289;                
KILL CONNECTION 3264;               
KILL CONNECTION 193;                
KILL CONNECTION 294;                
KILL CONNECTION 194;                
KILL CONNECTION 304;                
KILL CONNECTION 198;                
KILL CONNECTION 302;                
KILL CONNECTION 195;                
KILL CONNECTION 322;                
KILL CONNECTION 199;                
KILL CONNECTION 325;                
KILL CONNECTION 200;                
KILL CONNECTION 326;                
KILL CONNECTION 103;                
KILL CONNECTION 201;                
KILL CONNECTION 327;