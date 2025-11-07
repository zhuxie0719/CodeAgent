from flask import Flask, Blueprint

app = Flask(__name__)
parent = Blueprint('parent', __name__, url_prefix='/child')
child = Blueprint('child', __name__, url_prefix='/parent')

@child.route('/')
def index():
    return 'hello'

print("Parent blueprint url_prefix:", parent.url_prefix)
print("Child blueprint url_prefix:", child.url_prefix)

parent.register_blueprint(child)
app.register_blueprint(parent)

print("\nFlask routes:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint:20} {rule.methods} {rule.rule}")

print("\nExpected: /child/parent/")
print("Actual:", [rule.rule for rule in app.url_map.iter_rules() if 'index' in rule.endpoint][0])
