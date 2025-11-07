class Flask:
    def __init__(self, name):
        self.name = name
    
    def route(self, rule):
        def decorator(f):
            return f
        return decorator
    
    def run(self, **kwargs):
        print("Running Flask app")
