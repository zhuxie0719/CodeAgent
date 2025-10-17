#!/usr/bin/env python3
"""
简单的Flask应用示例
用于动态测试
"""

from flask import Flask, render_template, jsonify, request, url_for, session, redirect
import json
import time

app = Flask(__name__)
app.secret_key = 'test_secret_key'

# 模拟数据
users = [
    {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
    {"id": 2, "name": "李四", "email": "lisi@example.com"},
    {"id": 3, "name": "王五", "email": "wangwu@example.com"}
]

@app.route('/')
def index():
    """首页"""
    return render_template('index.html', users=users)

@app.route('/api/users')
def api_users():
    """获取用户列表API"""
    return jsonify(users)

@app.route('/api/users/<int:user_id>')
def api_user(user_id):
    """获取单个用户API"""
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "用户不存在"}), 404

@app.route('/test')
def test_page():
    """测试页面"""
    return "这是一个测试页面"

@app.route('/error')
def error_page():
    """故意出错的页面"""
    raise ValueError("这是一个测试错误")

@app.route('/slow')
def slow_page():
    """模拟慢页面"""
    time.sleep(2)  # 模拟慢操作
    return "这是一个慢页面"

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的验证逻辑
        if username == 'admin' and password == 'password':
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """仪表板"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    """登出"""
    session.pop('user', None)
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
