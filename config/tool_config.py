from typing import Dict, Any
from config.base_config import BaseConfig


class ToolConfig(BaseConfig):
    """工具配置类，管理各种工具的配置"""

    def __init__(self):
        """初始化工具配置类"""
        super().__init__("tool.json")

    def validate(self) -> bool:
        """验证工具配置

        Returns:
            bool: 验证是否通过
        """
        if not self.config_data:
            print("工具配置为空")
            return False

        required_sections = ["selenium", "appium", "jmeter", "postman"]
        for section in required_sections:
            if section not in self.config_data:
                print(f"工具配置缺少必要的部分: {section}")
                return False

        return True

    def get_selenium_config(self) -> Dict[str, Any]:
        """获取Selenium配置

        Returns:
            Dict[str, Any]: Selenium配置
        """
        return self.config_data.get("selenium", {})

    def get_appium_config(self) -> Dict[str, Any]:
        """获取Appium配置

        Returns:
            Dict[str, Any]: Appium配置
        """
        return self.config_data.get("appium", {})

    def get_jmeter_config(self) -> Dict[str, Any]:
        """获取JMeter配置

        Returns:
            Dict[str, Any]: JMeter配置
        """
        return self.config_data.get("jmeter", {})

    def get_postman_config(self) -> Dict[str, Any]:
        """获取Postman配置

        Returns:
            Dict[str, Any]: Postman配置
        """
        return self.config_data.get("postman", {})

    def get_git_config(self) -> Dict[str, Any]:
        """获取Git配置

        Returns:
            Dict[str, Any]: Git配置
        """
        return self.config_data.get("git", {})

    def get_jenkins_config(self) -> Dict[str, Any]:
        """获取Jenkins配置

        Returns:
            Dict[str, Any]: Jenkins配置
        """
        return self.config_data.get("jenkins", {})

    def get_docker_config(self) -> Dict[str, Any]:
        """获取Docker配置

        Returns:
            Dict[str, Any]: Docker配置
        """
        return self.config_data.get("docker", {})
