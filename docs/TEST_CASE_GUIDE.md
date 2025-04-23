# 测试用例编写指南

## 目录
1. [测试用例结构](#测试用例结构)
2. [Web测试用例](#web测试用例)
3. [API测试用例](#api测试用例)
4. [移动端测试用例](#移动端测试用例)
5. [最佳实践](#最佳实践)

## 测试用例结构

### 基本结构
每个测试用例应该包含以下部分：
```python
from testcases.base_test import BaseTest

class MyTestCase(BaseTest):
    def __init__(self):
        super().__init__("test_case_name")
        
    def run_test(self):
        try:
            # 测试步骤
            self.log_step("步骤1")
            # 执行操作
            
            self.log_step("步骤2")
            # 执行操作
            
            # 验证结果
            self.log_result(True, "测试通过")
        except Exception as e:
            self.log_result(False, str(e))
```

### 测试步骤
- 使用 `log_step` 记录每个测试步骤
- 步骤描述应该清晰明确
- 包含必要的等待和验证

### 错误处理
- 使用 try-except 捕获异常
- 记录详细的错误信息
- 保存错误截图

## Web测试用例

### Selenium测试用例
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WebTestCase(BaseTest):
    def __init__(self):
        super().__init__("web_test")
        self.driver = None
        
    def setup(self):
        # 初始化WebDriver
        self.driver = create_selenium_driver()
        
    def run_test(self):
        try:
            self.log_step("访问登录页面")
            self.driver.get("https://example.com/login")
            
            self.log_step("输入用户名和密码")
            username = self.driver.find_element(By.ID, "username")
            password = self.driver.find_element(By.ID, "password")
            username.send_keys("test_user")
            password.send_keys("test_password")
            
            self.log_step("点击登录按钮")
            login_button = self.driver.find_element(By.ID, "login")
            login_button.click()
            
            # 验证登录成功
            self.log_step("验证登录成功")
            welcome_text = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "welcome"))
            )
            assert "欢迎" in welcome_text.text
            
            self.log_result(True, "登录测试通过")
        except Exception as e:
            self.take_screenshot("error")
            self.log_result(False, str(e))
        finally:
            if self.driver:
                self.driver.quit()
```

### Playwright测试用例
```python
from playwright.sync_api import sync_playwright

class PlaywrightTestCase(BaseTest):
    def __init__(self):
        super().__init__("playwright_test")
        
    def run_test(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            
            try:
                self.log_step("访问搜索页面")
                page.goto("https://example.com/search")
                
                self.log_step("输入搜索关键词")
                page.fill("#search-input", "测试关键词")
                
                self.log_step("点击搜索按钮")
                page.click("#search-button")
                
                # 验证搜索结果
                self.log_step("验证搜索结果")
                results = page.locator(".search-result")
                assert results.count() > 0
                
                self.log_result(True, "搜索测试通过")
            except Exception as e:
                self.take_screenshot("error")
                self.log_result(False, str(e))
            finally:
                browser.close()
```

## API测试用例

### 基本API测试
```python
import requests

class APITestCase(BaseTest):
    def __init__(self):
        super().__init__("api_test")
        
    def run_test(self):
        try:
            self.log_step("发送GET请求")
            response = requests.get("https://api.example.com/users")
            assert response.status_code == 200
            
            self.log_step("验证响应数据")
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            
            self.log_result(True, "API测试通过")
        except Exception as e:
            self.log_result(False, str(e))
```

### 带认证的API测试
```python
class AuthAPITestCase(BaseTest):
    def __init__(self):
        super().__init__("auth_api_test")
        
    def run_test(self):
        try:
            # 获取认证token
            self.log_step("获取认证token")
            auth_response = requests.post(
                "https://api.example.com/auth",
                json={"username": "test", "password": "test123"}
            )
            token = auth_response.json()["token"]
            
            # 使用token访问API
            self.log_step("访问受保护的API")
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                "https://api.example.com/protected",
                headers=headers
            )
            assert response.status_code == 200
            
            self.log_result(True, "认证API测试通过")
        except Exception as e:
            self.log_result(False, str(e))
```

## 移动端测试用例

### Appium测试用例
```python
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy

class MobileTestCase(BaseTest):
    def __init__(self):
        super().__init__("mobile_test")
        self.driver = None
        
    def setup(self):
        # 初始化Appium driver
        desired_caps = {
            "platformName": "Android",
            "deviceName": "emulator-5554",
            "appPackage": "com.example.app",
            "appActivity": ".MainActivity"
        }
        self.driver = webdriver.Remote(
            "http://localhost:4723/wd/hub",
            desired_caps
        )
        
    def run_test(self):
        try:
            self.log_step("等待应用启动")
            time.sleep(5)
            
            self.log_step("点击登录按钮")
            login_button = self.driver.find_element(
                AppiumBy.ID,
                "com.example.app:id/login_button"
            )
            login_button.click()
            
            self.log_step("输入用户名和密码")
            username = self.driver.find_element(
                AppiumBy.ID,
                "com.example.app:id/username"
            )
            password = self.driver.find_element(
                AppiumBy.ID,
                "com.example.app:id/password"
            )
            username.send_keys("test_user")
            password.send_keys("test_password")
            
            self.log_step("点击提交按钮")
            submit_button = self.driver.find_element(
                AppiumBy.ID,
                "com.example.app:id/submit"
            )
            submit_button.click()
            
            # 验证登录成功
            self.log_step("验证登录成功")
            welcome_text = self.driver.find_element(
                AppiumBy.ID,
                "com.example.app:id/welcome_text"
            )
            assert "欢迎" in welcome_text.text
            
            self.log_result(True, "移动端登录测试通过")
        except Exception as e:
            self.take_screenshot("error")
            self.log_result(False, str(e))
        finally:
            if self.driver:
                self.driver.quit()
```

## 最佳实践

### 1. 测试用例设计
- 每个测试用例应该只测试一个功能点
- 测试用例应该独立，不依赖其他测试用例
- 测试用例应该包含清晰的步骤描述
- 测试用例应该包含必要的验证点

### 2. 错误处理
- 使用 try-except 捕获异常
- 记录详细的错误信息
- 保存错误截图
- 清理测试环境

### 3. 日志记录
- 记录每个测试步骤
- 记录关键操作的结果
- 记录错误信息
- 使用合适的日志级别

### 4. 截图管理
- 在关键步骤保存截图
- 在错误发生时保存截图
- 使用有意义的截图名称
- 定期清理过期截图

### 5. 测试数据管理
- 使用配置文件管理测试数据
- 避免硬编码测试数据
- 使用随机数据避免冲突
- 清理测试数据

### 6. 性能优化
- 减少不必要的等待
- 使用显式等待替代隐式等待
- 优化测试用例执行顺序
- 使用并行执行提高效率 