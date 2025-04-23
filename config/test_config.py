from typing import Dict, Any
from config.base_config import BaseConfig


class TestConfig(BaseConfig):
    """测试配置类，管理测试相关的配置"""

    def __init__(self):
        """初始化测试配置类"""
        super().__init__("test.json")

    def validate(self) -> bool:
        """验证测试配置

        Returns:
            bool: 验证是否通过
        """
        if not self.config_data:
            print("测试配置为空")
            return False

        required_sections = ["web", "api", "mobile", "performance", "report", "logging"]
        for section in required_sections:
            if section not in self.config_data:
                print(f"测试配置缺少必要的部分: {section}")
                return False

        return True

    def get_web_config(self) -> Dict[str, Any]:
        """获取Web测试配置

        Returns:
            Dict[str, Any]: Web测试配置
        """
        return self.config_data.get("web", {})

    def get_api_config(self) -> Dict[str, Any]:
        """获取API测试配置

        Returns:
            Dict[str, Any]: API测试配置
        """
        return self.config_data.get("api", {})

    def get_mobile_config(self) -> Dict[str, Any]:
        """获取移动端测试配置

        Returns:
            Dict[str, Any]: 移动端测试配置
        """
        return self.config_data.get("mobile", {})

    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能测试配置

        Returns:
            Dict[str, Any]: 性能测试配置
        """
        return self.config_data.get("performance", {})

    def get_concurrency_config(self) -> Dict[str, Any]:
        """获取并发测试配置

        Returns:
            Dict[str, Any]: 并发测试配置
        """
        return self.config_data.get("concurrency", {})

    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置

        Returns:
            Dict[str, Any]: 报告配置
        """
        return self.config_data.get("report", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置

        Returns:
            Dict[str, Any]: 日志配置
        """
        return self.config_data.get("logging", {})
