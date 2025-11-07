from flask import Flask, request, send_file, jsonify
import os
import sys
import subprocess
import pickle

app = Flask(__name__)

@app.route('/file', methods=['GET'])
def read_file():
    filename = request.args.get('name', '')
    
    file_path = os.path.join('uploads', filename)
    file_path = os.path.normpath(file_path)
    
    if not file_path.startswith('uploads'):
        return jsonify({'error': '非法文件路径'}), 403
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path)
    else:
        return jsonify({'error': '文件不存在'}), 404

@app.route('/ping', methods=['GET'])
def ping():
    host = request.args.get('host', '127.0.0.1')
    
    if not host.replace('.', '').isdigit():
        return jsonify({'error': '非法主机地址'}), 400
    
    command = ["ping", "-n", "4", host]
    result = subprocess.run(command, shell=False, capture_output=True, text=True)
    
    return jsonify({
        'command': ' '.join(command),
        'output': result.stdout,
        'error': result.stderr
    })

@app.route('/data', methods=['POST'])
def process_data():
    data = request.form.get('data', '')
    
    try:
        import base64
        decoded_data = base64.b64decode(data)
        obj = pickle.loads(decoded_data)
        return jsonify({'message': '数据已处理', 'type': str(type(obj))})
    except (pickle.UnpicklingError, EOFError, AttributeError, ImportError, IndexError, TypeError, ValueError) as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 400

@app.route('/admin', methods=['GET'])
def admin():
    username = request.args.get('username', '')
    password = request.args.get('password', '')
    
    if username == 'admin' and password == 'admin123':
        return jsonify({'message': '登录成功'})
    else:
        return jsonify({'error': '登录失败！用户名或密码错误'}), 401

@app.route('/')
def index():
    return '''
    <html>
    <head><title>漏洞测试页面</title></head>
    <body>
        <h1>漏洞测试功能</h1>
        <ul>
            <li><a href="/file?name=test.txt">缺陷1: 路径遍历漏洞 (/file)</a></li>
            <li><a href="/ping?host=127.0.0.1">缺陷2: 命令注入漏洞 (/ping)</a></li>
            <li><a href="/data">缺陷3: 不安全的反序列化 (/data)</a></li>
            <li><a href="/admin?username=test&password=test">缺陷4: 敏感信息泄露 (/admin)</a></li>
        </ul>
        <h2>测试说明：</h2>
        <p><strong>缺陷1 - 路径遍历：</strong> 尝试 <code>/file?name=../../etc/passwd</code> 或 <code>/file?name=../../windows/win.ini</code></p>
        <p><strong>缺陷2 - 命令注入：</strong> 尝试 <code>/ping?host=127.0.0.1 && whoami</code> 或 <code>/ping?host=127.0.0.1 | dir</code></p>
        <p><strong>缺陷3 - 反序列化：</strong> 使用pickle序列化恶意对象进行攻击</p>
        <p><strong>缺陷4 - 信息泄露：</strong> 查看错误响应中的敏感信息</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)