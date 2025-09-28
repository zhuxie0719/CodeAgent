// JavaScript测试文件 - 包含各种缺陷

// XSS漏洞风险
function displayUserInput(userInput) {
    document.getElementById('output').innerHTML = userInput;
    document.write(userInput);
}

// 未使用的变量
var unusedVariable = "This variable is never used";

// 不安全的操作
function unsafeOperation() {
    var userInput = "alert('XSS')";
    eval(userInput);
}

// 缺少错误处理
function divideNumbers(a, b) {
    return a / b; // 没有检查除零
}

console.log("JavaScript测试文件加载完成");
