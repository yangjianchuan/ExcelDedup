# 使用官方Python镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p /app/uploads
RUN chmod 777 /app/uploads

# 暴露端口
EXPOSE 5000

# 安装gunicorn
RUN pip install gunicorn==20.1.0

# 运行应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]