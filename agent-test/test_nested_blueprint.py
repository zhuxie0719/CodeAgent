from flask import Flask, Blueprint

app = Flask(__name__)
parent = Blueprint('parent', __name__, url_prefix='/parent')
child = Blueprint('child', __name__, url_prefix='/child')

@child.route('/')
def index():
    return 'hello'

parent.register_blueprint(child)
app.register_blueprint(parent)

if __name__ == '__main__':
    with app.app_context():
        print("Routes:")
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule.rule}")
