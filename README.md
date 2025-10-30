---
title: ExcelDedup
emoji: ⚡
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
license: mit
short_description: 这是一个基于Flask的Web应用程序，用于对Excel文件进行去重处理。
app_port: 5000
---

# Excel Deduplicator (ExcelDedup)

这是一个基于Flask的Web应用程序，用于对Excel文件进行去重处理。

## 功能特性
- 上传Excel文件并自动去重
- 生成带时间戳的去重结果文件
- 自动清理上传的临时文件
- 提供文件下载功能
- 支持手动清理缓存

## 技术栈
- Python 3.x
- Flask
- Pandas
- Docker（可选）

## 运行要求

```
Flask==2.3.2
pandas==2.3.3
numpy==2.3.4
openpyxl==3.1.2
gunicorn==20.1.0
```

## 使用方法

### 设置Python虚拟环境（推荐）
1. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
2. 激活虚拟环境：
   ```bash
   # Windows
   source venv/Scripts/activate

   # macOS/Linux
   source venv/bin/activate
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 本地运行
1. 启动应用：
   ```bash
   python app.py
   ```
   或者使用Flask命令：
   ```bash
   flask run
   ```
2. 访问 http://localhost:5000

### Docker运行
1. 构建镜像：
   ```bash
   docker-compose build
   ```
2. 启动容器：
   ```bash
   docker-compose up
   ```
3. 访问 http://localhost:5000

## 文件清理
- 系统会自动清理5分钟前的上传文件
- 可通过"清理缓存"按钮手动清理所有上传文件

## 注意事项
- 仅支持.xlsx格式文件
- 上传文件大小限制由Flask配置决定
- 去重基于整行数据比较

## 在线演示
- [演示地址](https://dongsiqie-exceldedup.hf.space/)
- [抱脸huggingface一键部署](https://huggingface.co/spaces/dongsiqie/ExcelDedup/settings?duplicate=true&visibility=public)