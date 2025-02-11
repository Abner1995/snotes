# 常用命令 

## 删除所有未提交的本地更改  
```bash  
git reset --hard HEAD
```  

```bash
git add .
git commit -m "Initial commit"
git remote add origin https://gitee.com/shanghai-hongqian/fangtaohui.git
git push -u origin master
```  

## 强制区分文件名的大小写
```bash  
git config --global core.ignorecase false
```  

## 忽略文件跟踪
```bash  
git rm --cached dbmigration/config/phoenix.php
git add .gitignore
git commit -m "Add files to .gitignore"
```  