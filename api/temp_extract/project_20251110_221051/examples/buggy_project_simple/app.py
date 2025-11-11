from flask import Flask, request, jsonify

app = Flask(__name__)


@app.get("/user")
def get_user():
    # 未验证的请求参数 + 动态执行 + 路径拼接读取
    user_id = request.args["id"]  # unsafe_request_params
    calc = eval(request.args.get("data", "0"))  # eval: critical
    with open(f"users/{user_id}.txt", "r", encoding="utf-8") as f:  # unsafe_file_read
        content = f.read()
    try:
        value = 1 / int(request.args.get("div", "0"))  # division_by_zero
    except Exception:  # broad and empty except
        pass  # empty_except
    return jsonify({"ok": True, "data": content, "calc": calc})


@app.post("/upload")
def upload():
    # 未校验文件类型/大小/内容
    f = request.files["file"]  # unsafe_file_upload
    f.save("/tmp/" + f.filename)  # 可能存在路径穿越
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)


