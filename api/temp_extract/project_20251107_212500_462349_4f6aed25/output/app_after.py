from flask import Flask, request, render_template_string, jsonify
import sqlite3
import os

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)''')
    cursor.execute('''INSERT OR IGNORE INTO users (name, email) VALUES ('admin', 'admin@test.com')''')
    conn.commit()
    
    sql = "SELECT * FROM users WHERE name LIKE ?"
    cursor.execute(sql, ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    
    return jsonify({'results': results, 'query': sql})

@app.route('/comment', methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        user_comment = request.form.get('comment', '')
        template = '''
        <html>
        <head><title>评论</title></head>
        <body>
            <h1>您的评论：</h1>
            <p>{{ comment }}</p>
            <form method="POST">
                <textarea name="comment" placeholder="输入评论"></textarea><br>
                <input type="submit" value="提交">
            </form>
        </body>
        </html>
        '''
        return render_template_string(template, comment=user_comment)
    else:
        template = '''
        <html>
        <head><title>评论</title></head>
        <body>
            <h1>发表评论</h1>
            <form method="POST">
                <textarea name="comment" placeholder="输入评论"></textarea><br>
                <input type="submit" value="提交">
            </form>
        </body>
        </html>
        '''
        return render_template_string(template, comment='')

@app.route('/template', methods=['GET', 'POST'])
def template_render():
    if request.method == 'POST':
        template_content = request.form.get('template', '')
        data = request.form.get('data', '')
        
        try:
            rendered = render_template_string(template_content, data=data)
            return f'''
            <html>
            <head><title>模板渲染结果</title></head>
            <body>
                <h1>渲染结果：</h1>
                <pre>{rendered}</pre>
                <hr>
                <form method="POST">
                    <label>模板内容：</label><br>
                    <textarea name="template" rows="5" cols="50">{{ data }}</textarea><br>
                    <label>数据：</label><br>
                    <input type="text" name="data" value=""><br>
                    <input type="submit" value="渲染">
                </form>
            </body>
            </html>
            '''
        except (ValueError, TypeError, SyntaxError, NameError, AttributeError, KeyError, IndexError) as e:
            return f'错误: {str(e)}'
    else:
        return '''
        <html>
        <head><title>模板渲染</title></head>
        <body>
            <h1>模板渲染工具</h1>
            <form method="POST">
                <label>模板内容：</label><br>
                <textarea name="template" rows="5" cols="50">Hello {{ data }}</textarea><br>
                <label>数据：</label><br>
                <input type="text" name="data" value="World"><br>
                <input type="submit" value="渲染">
            </form>
        </body>
        </html>
        '''

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Flask安全测试项目</title></head>
    <body>
        <h1>Flask安全测试项目</h1>
        <ul>
            <li><a href="/search?q=admin">缺陷1: SQL注入漏洞 (/search)</a></li>
            <li><a href="/comment">缺陷2: XSS漏洞 (/comment)</a></li>
            <li><a href="/template">缺陷3: 服务器端模板注入 (SSTI) (/template)</a></li>
        </ul>
        <h2>测试说明：</h2>
        <p><strong>缺陷1 - SQL注入：</strong> 尝试在搜索参数中使用SQL注入，如: <code>/search?q=' OR '1'='1</code></p>
        <p><strong>缺陷2 - XSS：</strong> 在评论框中输入 <code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></p>
        <p><strong>缺陷3 - SSTI：</strong> 尝试模板注入，如: <code>{{ config }}</code> 或 <code>{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}</code></p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)