// test_javascript.js - JavaScript测试文件

// 硬编码的API密钥
const API_KEY = "sk-1234567890abcdef";

function badFunction() {
    // 缺少错误处理
    const data = JSON.parse(userInput); // 可能抛出异常
    
    // 不安全的eval使用
    eval("console.log('Hello')"); // 安全风险
    
    // 内存泄漏 - 闭包引用
    const bigArray = new Array(1000000).fill(0);
    return function() {
        return bigArray.length; // 闭包持有大数组引用
    };
}

// 不安全的DOM操作
function updateDOM() {
    const element = document.getElementById('user-input');
    element.innerHTML = userInput; // XSS风险
}