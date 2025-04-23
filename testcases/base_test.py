import os
import time
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime


class BaseTest:
    """测试用例基类，提供通用的测试功能"""

    def __init__(self, test_name: str):
        """初始化测试用例

        Args:
            test_name: 测试用例名称
        """
        self.test_name = test_name
        self.start_time = None
        self.end_time = None
        self.steps = []
        self.attachments = []
        self.result = None
        self.result_message = ""

        # 设置日志
        self.logger = logging.getLogger(f"test.{test_name}")
        self.setup_logging()

    def setup_logging(self):
        """设置日志"""
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            # 文件处理器
            log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(os.path.join(log_dir, f"{self.test_name}.log"))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

            self.logger.setLevel(logging.INFO)

    def setup(self):
        """测试前置处理"""
        self.logger.info(f"开始测试: {self.test_name}")
        self.start_time = datetime.now()

    def teardown(self):
        """测试后置处理"""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        self.logger.info(f"结束测试: {self.test_name}, 耗时: {duration}秒, 结果: {self.result}")

    def run(self):
        """运行测试"""
        try:
            self.setup()
            self.run_test()
        except Exception as e:
            self.logger.error(f"测试执行异常: {str(e)}", exc_info=True)
            self.log_result(False, f"测试异常: {str(e)}")
        finally:
            self.teardown()

        return self.get_result()

    def run_test(self):
        """执行测试，需要子类实现"""
        raise NotImplementedError("子类必须实现run_test方法")

    def log_step(self, step_description: str):
        """记录测试步骤

        Args:
            step_description: 步骤描述
        """
        self.logger.info(f"步骤: {step_description}")
        self.steps.append(step_description)

    def log_result(self, success: bool, message: str):
        """记录测试结果

        Args:
            success: 是否成功
            message: 结果消息
        """
        self.result = "PASS" if success else "FAIL"
        self.result_message = message
        log_method = self.logger.info if success else self.logger.error
        log_method(f"结果: {self.result} - {message}")

    def take_screenshot(self, name: str) -> str:
        """保存截图

        Args:
            name: 截图名称

        Returns:
            str: 截图路径
        """
        # 这个方法在子类中具体实现，这里只是一个占位符
        return ""

    def add_attachment(self, name: str, url: str):
        """添加附件

        Args:
            name: 附件名称
            url: 附件URL
        """
        self.attachments.append({"name": name, "url": url})
        self.logger.info(f"添加附件: {name} - {url}")

    def get_result(self) -> Dict[str, Any]:
        """获取测试结果

        Returns:
            Dict[str, Any]: 测试结果
        """
        return {
            "test_name": self.test_name,
            "status": self.result or "UNKNOWN",
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S") if self.start_time else "",
            "end_time": self.end_time.strftime("%Y-%m-%d %H:%M:%S") if self.end_time else "",
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0,
            "steps": self.steps,
            "attachments": self.attachments,
            "message": self.result_message
        }
