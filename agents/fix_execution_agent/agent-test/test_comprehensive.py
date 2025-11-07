# Test various import patterns to ensure the fix is robust
from flask import Flask, render_template, request, flash, send_file
from flask import Flask as F, render_template as rt

# Test usage of imported items
app1 = Flask(__name__)
app2 = F(__name__)

result1 = render_template('index.html')
result2 = rt('home.html')

req = request
flash_msg = flash("Test message")
file_result = send_file("test.txt")

print("All imports and usage work correctly!")
