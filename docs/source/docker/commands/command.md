# docker  

```shell    
export DOWNLOAD_URL="http://mirrors.163.com/docker-ce"
export DOWNLOAD_URL="https://docker.1ms.run"

docker ps

# 查询某个容器  
docker ps | grep prometheus  

# 查看容器的详细信息，包括挂载卷的信息  
docker inspect 8b552af98fa0  

# 在输出的信息中，查找Mounts部分，可以看到挂载的卷信息，其中包括Source和Destination。Source是宿主机上的路径，而Destination是容器内的路径。  
# 例如，如果配置文件被挂载到容器内的/etc/prometheus/prometheus.yml，那么Destination应该是/etc/prometheus/prometheus.yml。  

# 查询容器的配置文件  
docker exec -it 8b552af98fa0 ls -l /prometheus/

docker exec -it 8b552af98fa0 find / -name prometheus.yml

# 查询容器的log  
docker logs mysqld_exporter  

# 进入容器
docker exec -it 34345f42cfed bash

docker run --name myredis -v E:\docker\redis\redis.conf:/usr/local/etc/redis/redis.conf -d redis redis-server /usr/local/etc/redis/redis.conf

docker run --name myredis -v E:\docker\redis\redis.conf:/usr/local/etc/redis/redis.conf -p 6379:6379 -d redis redis-server /usr/local/etc/redis/redis.conf
``` 