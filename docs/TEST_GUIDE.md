# 测试指南

## 测试类型

### 1. Web自动化测试

#### 配置说明
```json
{
    "web": {
        "browser": "chrome",
        "headless": false,
        "implicit_wait": 10,
        "page_load_timeout": 30,
        "script_timeout": 30,
        "screenshot_dir": "screenshots/web",
        "window_size": {
            "width": 1920,
            "height": 1080
        }
    }
}
```

#### 示例代码
```python
from testcases.utils.web_utils import WebUtils
from selenium.webdriver.common.by import By

def test_login():
    web_utils = WebUtils()
    try:
        # 打开登录页面
        web_utils.open_url("https://example.com/login")
        
        # 输入用户名和密码
        web_utils.input_text(By.ID, "username", "test_user")
        web_utils.input_text(By.ID, "password", "test_pass")
        
        # 点击登录按钮
        web_utils.click(By.ID, "login_button")
        
        # 验证登录成功
        assert web_utils.is_element_present(By.ID, "welcome_message")
        
    finally:
        web_utils.quit()
```

### 2. API自动化测试

#### 配置说明
```json
{
    "api": {
        "timeout": 30,
        "verify_ssl": true,
        "retry_times": 3,
        "retry_interval": 1,
        "log_response": true,
        "log_headers": false
    }
}
```

#### 示例代码
```python
from testcases.utils.api_utils import ApiUtils

def test_user_management():
    api_utils = ApiUtils()
    try:
        # 获取认证令牌
        token = api_utils.get_auth_token("username", "password")
        
        # 设置请求头
        api_utils.set_headers({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })
        
        # 创建用户
        response = api_utils.send_request(
            "POST",
            "/users",
            json={"name": "test_user", "email": "test@example.com"}
        )
        
        # 验证响应
        assert response.status_code == 201
        assert response.json()["name"] == "test_user"
        
    finally:
        api_utils.cleanup()
```

### 3. 移动端自动化测试

#### 配置说明
```json
{
    "mobile": {
        "platform": "android",
        "device_name": "emulator-5554",
        "app_package": "com.example.app",
        "app_activity": "com.example.app.MainActivity",
        "app_path": "apps/example.apk",
        "implicit_wait": 10,
        "screenshot_dir": "screenshots/mobile"
    }
}
```

#### 示例代码
```python
from testcases.utils.mobile_utils import MobileUtils
from appium.webdriver.common.mobileby import MobileBy

def test_app_settings():
    mobile_utils = MobileUtils()
    try:
        # 打开设置页面
        mobile_utils.find_element(MobileBy.ID, "settings_button").click()
        
        # 修改通知设置
        mobile_utils.find_element(MobileBy.ID, "notifications_switch").click()
        
        # 验证设置已保存
        assert mobile_utils.find_element(
            MobileBy.ID, "notifications_switch"
        ).get_attribute("checked") == "true"
        
    finally:
        mobile_utils.quit()
```

### 4. 性能测试

#### 配置说明
```json
{
    "performance": {
        "thresholds": {
            "response_time": 3.0,
            "cpu_usage": 80,
            "memory_usage": 80,
            "error_rate": 0.01
        },
        "duration": 300,
        "users": 100,
        "ramp_up": 60
    }
}
```

#### 示例代码
```python
from testcases.utils.performance_utils import PerformanceUtils

def test_api_performance():
    perf_utils = PerformanceUtils()
    try:
        # 开始性能测试
        perf_utils.start_measurement()
        
        # 执行API请求
        response_time = perf_utils.measure_response_time(
            lambda: api_utils.send_request("GET", "/users")
        )
        
        # 测量资源使用
        cpu_usage = perf_utils.measure_cpu_usage()
        memory_usage = perf_utils.measure_memory_usage()
        
        # 验证性能指标
        assert response_time <= 3.0
        assert cpu_usage <= 80
        assert memory_usage <= 80
        
    finally:
        perf_utils.stop_measurement()
```

### 5. 并发测试

#### 配置说明
```json
{
    "concurrency": {
        "max_threads": 10,
        "max_iterations": 100,
        "thread_delay": 1.0,
        "timeout": 300
    }
}
```

#### 示例代码
```python
from testcases.utils.concurrency_utils import ConcurrencyUtils

def test_concurrent_registration():
    concurrency_utils = ConcurrencyUtils()
    try:
        # 设置并发参数
        concurrency_utils.set_thread_count(10)
        concurrency_utils.set_iterations(100)
        
        # 定义测试函数
        def register_user(user_id):
            web_utils = WebUtils()
            try:
                web_utils.open_url("https://example.com/register")
                web_utils.input_text(
                    By.ID,
                    "username",
                    f"user_{user_id}"
                )
                web_utils.input_text(
                    By.ID,
                    "password",
                    f"pass_{user_id}"
                )
                web_utils.click(By.ID, "register_button")
                return True
            finally:
                web_utils.quit()
        
        # 执行并发测试
        results = concurrency_utils.run_concurrent_test(register_user)
        
        # 验证结果
        assert all(results)
        assert len(results) == 100
        
    finally:
        concurrency_utils.cleanup()
```

## 测试最佳实践

### 1. 测试用例设计
- 遵循AAA模式（Arrange-Act-Assert）
- 保持测试用例独立性
- 使用有意义的测试名称
- 添加必要的注释和文档

### 2. 错误处理
- 使用try-finally确保资源清理
- 捕获特定异常类型
- 提供详细的错误信息
- 保存失败时的截图和日志

### 3. 数据管理
- 使用测试数据工厂
- 避免硬编码数据
- 清理测试数据
- 使用随机数据避免冲突

### 4. 性能优化
- 减少不必要的等待
- 复用浏览器会话
- 优化测试数据量
- 使用并行执行

### 5. 报告生成
- 包含详细的测试信息
- 添加截图和日志
- 生成趋势分析
- 提供问题追踪链接

## 常见问题

### 1. 环境配置
- 确保所有依赖已安装
- 检查配置文件路径
- 验证环境变量设置
- 确认服务可用性

### 2. 测试失败
- 检查网络连接
- 验证元素定位
- 确认数据状态
- 查看错误日志

### 3. 性能问题
- 优化等待策略
- 减少资源占用
- 调整并发参数
- 监控系统资源

### 4. 报告问题
- 检查报告模板
- 验证数据格式
- 确认权限设置
- 清理过期报告 