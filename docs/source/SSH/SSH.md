# SSH 

## 本地电脑
```bash
# 生成密钥
ssh-keygen -t ed25519 -C "wan19950504@gmail.com"

# 本地查看你的公钥 在Windows的PowerShell中运行
type C:\Users\wan19\.ssh\id_ed25519.pub
```

## 服务器
检查 .ssh 目录内容，没有authorized_keys文件就去创建
```bash
ls -la ~/.ssh
```

直接查看 authorized_keys 文件
```bash
# 查看文件是否存在以及内容
cat ~/.ssh/authorized_keys

# 或者用更简单的方式
ls -l ~/.ssh/authorized_keys

# 或者直接用 echo 添加
echo "你的公钥内容（从本地复制的完整内容）" >> ~/.ssh/authorized_keys
```
