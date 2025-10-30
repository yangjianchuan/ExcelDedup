from flask import Flask, request, send_file, redirect
import pandas as pd
import os
import time
from threading import Thread
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}
CLEANUP_INTERVAL = 300  # 5分钟

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def cleanup_uploads():
    """定时清理uploads文件夹"""
    while True:
        time.sleep(CLEANUP_INTERVAL)
        try:
            for filename in os.listdir(app.config['UPLOAD_FOLDER']):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f'删除文件 {file_path} 失败: {e}')
        except Exception as e:
            print(f'清理uploads文件夹失败: {e}')

# 启动清理线程
cleanup_thread = Thread(target=cleanup_uploads)
cleanup_thread.daemon = True
cleanup_thread.start()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "没有选择文件"
            
        file = request.files['file']
        if file.filename == '':
            return "没有选择文件"
            
        if file and allowed_file(file.filename):
            # 确保上传目录存在
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            # 生成安全的文件名
            upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
            os.makedirs(upload_dir, exist_ok=True)
            filename = os.path.join(upload_dir, file.filename)
            file.save(filename)
            
            # 处理Excel文件
            df = pd.read_excel(filename)
            df_deduplicated = df.drop_duplicates()
            
            # 生成带时间戳的输出文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name, ext = os.path.splitext(file.filename)
            output_filename = os.path.join(upload_dir, f'{base_name}_{timestamp}{ext}')
            df_deduplicated.to_excel(output_filename, index=False)
            
            # 确保文件已写入
            if not os.path.exists(output_filename):
                raise FileNotFoundError(f"无法创建文件: {output_filename}")
            
            return f'''<!doctype html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>去重完成</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            padding: 0;
            max-width: 800px;
            margin: 0 auto;
        }}
        .result-container {{
            margin-top: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 8px;
            text-align: center;
        }}
        .btn {{
            display: inline-block;
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 10px;
        }}
        .btn-danger {{
            background: #e74c3c;
        }}
        .btn:hover {{
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <h1>去重完成</h1>
    <div class="result-container">
        <p>文件去重处理成功！</p>
        <button onclick="clearCache()" class="btn btn-danger">清理缓存</button>
        <script>
            function clearCache() {{
                fetch('/clear_cache', {{ method: 'POST' }})
                    .then(() => window.location.href = '/')
                    .catch(err => console.error(err));
            }}
        </script>
        <a href="/download/{os.path.basename(output_filename)}" class="btn">下载去重后的文件</a>
    </div>
</body>
</html>'''
    
    return '''
    <!doctype html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Excel去重工具</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                max-width: 800px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin: 30px 0;
            }
            .upload-form {
                background: #f5f5f5;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .upload-form input[type="file"] {
                margin: 10px 0;
                padding: 10px;
                width: 100%;
                box-sizing: border-box;
            }
            .upload-form input[type="submit"] {
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 16px;
            }
            .upload-form input[type="submit"]:hover {
                background: #2980b9;
            }
            .result-container {
                margin-top: 30px;
                padding: 20px;
                background: #ecf0f1;
                border-radius: 8px;
            }
            .btn {
                display: inline-block;
                padding: 10px 20px;
                background: #e74c3c;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                margin: 10px 0;
            }
            .btn:hover {
                background: #c0392b;
            }
            @media (max-width: 600px) {
                h1 {
                    font-size: 24px;
                }
                .upload-form {
                    padding: 15px;
                }
            }
        </style>
    </head>
    <body>
        <h1>Excel文件去重工具</h1>
        <div class="upload-form">
            <form method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".xlsx" required>
                <input type="submit" value="开始去重">
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/download/<filename>')
def download_file(filename):
    try:
        upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
        path = os.path.join(upload_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"文件 {filename} 不存在")
        return send_file(path, as_attachment=True)
    except Exception as e:
        return f"下载文件失败: {str(e)}", 500

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    try:
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f'删除文件 {file_path} 失败: {e}')
        return '''
        <!doctype html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>缓存已清理</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin-top: 50px;
                }
                .countdown {
                    font-size: 24px;
                    color: #2c3e50;
                    margin: 20px 0;
                }
            </style>
            <script>
                let count = 3;
                const countdown = document.getElementById('countdown');
                setInterval(() => {
                    count--;
                    countdown.innerText = count;
                    if (count === 0) {
                        window.location.href = '/';
                    }
                }, 1000);
            </script>
        </head>
        <body>
            <h1>缓存已成功清理</h1>
            <div class="countdown">
                将在 <span id="countdown">3</span> 秒后返回首页
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f'清理缓存失败: {e}'

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5600)