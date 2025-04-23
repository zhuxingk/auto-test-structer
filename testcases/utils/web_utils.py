import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from config.test_config import TestConfig
from config.tool_config import ToolConfig


class WebUtils:
    """Web测试工具类，封装Selenium操作"""

    def __init__(self, browser=None, headless=None):
        """初始化Web测试工具类

        Args:
            browser: 浏览器类型，如果为None则从配置中读取
            headless: 是否无头模式，如果为None则从配置中读取
        """
        self.test_config = TestConfig()
        self.test_config.load_config()

        self.tool_config = ToolConfig()
        self.tool_config.load_config()

        web_config = self.test_config.get_web_config()
        selenium_config = self.tool_config.get_selenium_config()

        self.browser = browser or web_config.get("browser", "chrome")
        self.headless = headless if headless is not None else web_config.get("headless", False)
        self.implicit_wait = web_config.get("implicit_wait", 10)
        self.page_load_timeout = web_config.get("page_load_timeout", 30)
        self.script_timeout = web_config.get("script_timeout", 30)

        self.screenshot_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            web_config.get("screenshot_dir", "screenshots/web")
        )
        os.makedirs(self.screenshot_dir, exist_ok=True)

        self.driver = self._init_driver()
        self._configure_driver()

    def _init_driver(self):
        """初始化WebDriver

        Returns:
            WebDriver: Selenium WebDriver实例
        """
        if self.browser.lower() == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            try:
                # 优先使用WebDriver Manager自动下载
                service = ChromeService(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            except Exception as e:
                print(f"自动下载Chrome驱动失败: {str(e)}，尝试使用本地驱动")
                # 继续 testcases/utils/web_utils.py 文件
                # 使用本地驱动
                selenium_config = self.tool_config.get_selenium_config()
                driver_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    selenium_config.get("webdriver_path", "drivers"),
                    selenium_config.get("chrome_driver", "chromedriver.exe")
                )
                service = ChromeService(driver_path)
                return webdriver.Chrome(service=service, options=options)

        elif self.browser.lower() == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")

            try:
                service = FirefoxService(GeckoDriverManager().install())
                return webdriver.Firefox(service=service, options=options)
            except Exception as e:
                print(f"自动下载Firefox驱动失败: {str(e)}，尝试使用本地驱动")
                selenium_config = self.tool_config.get_selenium_config()
                driver_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    selenium_config.get("webdriver_path", "drivers"),
                    selenium_config.get("firefox_driver", "geckodriver.exe")
                )
                service = FirefoxService(driver_path)
                return webdriver.Firefox(service=service, options=options)

        elif self.browser.lower() == "edge":
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless")

            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
                return webdriver.Edge(service=service, options=options)
            except Exception as e:
                print(f"自动下载Edge驱动失败: {str(e)}，尝试使用本地驱动")
                selenium_config = self.tool_config.get_selenium_config()
                driver_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    selenium_config.get("webdriver_path", "drivers"),
                    selenium_config.get("edge_driver", "msedgedriver.exe")
                )
                service = EdgeService(driver_path)
                return webdriver.Edge(service=service, options=options)
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser}")

        def _configure_driver(self):
            """配置WebDriver"""
            if self.driver:
                self.driver.implicitly_wait(self.implicit_wait)
                self.driver.set_page_load_timeout(self.page_load_timeout)
                self.driver.set_script_timeout(self.script_timeout)

                web_config = self.test_config.get_web_config()
                window_size = web_config.get("window_size", {"width": 1920, "height": 1080})
                self.driver.set_window_size(window_size.get("width"), window_size.get("height"))

        def open_url(self, url):
            """打开URL

            Args:
                url: 要打开的URL
            """
            self.driver.get(url)

        def find_element(self, by, value, timeout=None):
            """查找元素

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                WebElement: 找到的元素
            """
            timeout = timeout or self.implicit_wait
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))

        def find_elements(self, by, value, timeout=None):
            """查找多个元素

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                List[WebElement]: 找到的元素列表
            """
            timeout = timeout or self.implicit_wait
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_all_elements_located((by, value)))

        def click(self, by, value, timeout=None):
            """点击元素

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间
            """
            element = self.find_element(by, value, timeout)
            element.click()

        def input_text(self, by, value, text, timeout=None):
            """输入文本

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                text: 要输入的文本
                timeout: 超时时间，默认使用隐式等待时间
            """
            element = self.find_element(by, value, timeout)
            element.clear()
            element.send_keys(text)

        def get_text(self, by, value, timeout=None):
            """获取元素文本

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                str: 元素文本
            """
            element = self.find_element(by, value, timeout)
            return element.text

        def is_element_present(self, by, value, timeout=None):
            """判断元素是否存在

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                bool: 元素是否存在
            """
            try:
                self.find_element(by, value, timeout)
                return True
            except:
                return False

        def take_screenshot(self, name=None):
            """截图

            Args:
                name: 截图名称，默认使用时间戳

            Returns:
                str: 截图路径
            """
            if not name:
                name = f"screenshot_{int(time.time())}"

            file_name = f"{name}.png"
            file_path = os.path.join(self.screenshot_dir, file_name)

            self.driver.save_screenshot(file_path)
            return file_path

        def execute_script(self, script, *args):
            """执行JavaScript

            Args:
                script: JavaScript代码
                *args: 参数

            Returns:
                Any: 执行结果
            """
            return self.driver.execute_script(script, *args)

        def wait_for_element_visible(self, by, value, timeout=None):
            """等待元素可见

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                WebElement: 元素
            """
            timeout = timeout or self.implicit_wait
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located((by, value)))

        def wait_for_element_clickable(self, by, value, timeout=None):
            """等待元素可点击

            Args:
                by: 定位方式，如By.ID, By.XPATH等
                value: 定位值
                timeout: 超时时间，默认使用隐式等待时间

            Returns:
                WebElement: 元素
            """
            timeout = timeout or self.implicit_wait
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, value)))

        def quit(self):
            """关闭浏览器"""
            if self.driver:
                self.driver.quit()

        return None

