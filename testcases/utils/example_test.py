from selenium.webdriver.common.by import By
from testcases.base_test import BaseTest
from testcases.utils.web_utils import WebUtils
from testcases.utils.api_utils import ApiUtils


class WebLoginTest(BaseTest):
    """Web登录测试示例"""

    def __init__(self):
        """初始化Web登录测试"""
        super().__init__("web_login_test")
        self.web_utils = None

    def setup(self):
        """测试前置处理"""
        super().setup()
        self.web_utils = WebUtils(browser="chrome", headless=False)

    def run_test(self):
        """执行测试"""
        try:
            # 打开登录页面
            self.log_step("打开登录页面")
            self.web_utils.open_url("https://example.com/login")

            # 输入用户名和密码
            self.log_step("输入用户名")
            self.web_utils.input_text(By.ID, "username", "test_user")

            self.log_step("输入密码")
            self.web_utils.input_text(By.ID, "password", "test_password")

            # 继续 testcases/example_test.py 文件
            # 点击登录按钮
            self.log_step("点击登录按钮")
            self.web_utils.click(By.ID, "login_button")

            # 验证登录结果
            self.log_step("验证登录结果")
            # 这里假设登录成功后会显示欢迎信息
            if self.web_utils.is_element_present(By.ID, "welcome_message"):
                # 截图记录
                screenshot_path = self.web_utils.take_screenshot("login_success")
                self.add_attachment("登录成功截图", screenshot_path)
                self.log_result(True, "登录测试通过")
            else:
                # 截图记录
                screenshot_path = self.web_utils.take_screenshot("login_failed")
                self.add_attachment("登录失败截图", screenshot_path)
                self.log_result(False, "登录测试失败，未找到欢迎信息")
        except Exception as e:
            # 截图记录
            screenshot_path = self.web_utils.take_screenshot("login_error")
            self.add_attachment("错误截图", screenshot_path)
            self.log_result(False, f"登录测试异常: {str(e)}")

        def teardown(self):
            """测试后置处理"""
            if self.web_utils:
                self.web_utils.quit()
            super().teardown()

        class ApiUserTest(BaseTest):
            """API用户操作测试示例"""

            def __init__(self):
                """初始化API用户操作测试"""
                super().__init__("api_user_test")
                self.api_utils = None

            def setup(self):
                """测试前置处理"""
                super().setup()
                self.api_utils = ApiUtils()

            def run_test(self):
                """执行测试"""
                try:
                    # 获取认证令牌
                    self.log_step("获取认证令牌")
                    token = "test_token"  # 实际项目中应该调用 self.api_utils.get_auth_token("username", "password")

                    # 设置请求头
                    self.log_step("设置请求头")
                    self.api_utils.set_headers({
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    })

                    # 创建用户
                    self.log_step("创建用户")
                    user_data = {
                        "name": "Test User",
                        "email": "test@example.com",
                        "role": "user"
                    }

                    # 这里使用 try-except 模拟请求，实际项目中应该发送真实请求
                    try:
                        # 模拟响应
                        response = type('Response', (), {
                            'status_code': 201,
                            'json': lambda: {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"},
                            'text': '{"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"}'
                        })

                        # 验证响应状态码
                        self.log_step("验证响应状态码")
                        if response.status_code == 201:
                            # 验证响应内容
                            self.log_step("验证响应内容")
                            user = response.json()
                            if user.get("name") == user_data["name"] and user.get("email") == user_data["email"]:
                                self.log_result(True, "创建用户测试通过")
                            else:
                                self.log_result(False, "创建用户测试失败，响应内容不匹配")
                        else:
                            self.log_result(False, f"创建用户测试失败，状态码: {response.status_code}")
                    except Exception as e:
                        self.log_result(False, f"API请求异常: {str(e)}")
                except Exception as e:
                    self.log_result(False, f"测试执行异常: {str(e)}")

            def teardown(self):
                """测试后置处理"""
                if self.api_utils:
                    self.api_utils.cleanup()
                super().teardown()

