from typing import Dict, Any
from config.base_config import BaseConfig


class EnvironmentConfig(BaseConfig):
    """环境配置类，管理不同环境的配置"""

    def __init__(self):
        """初始化环境配置类"""
        super().__init__("environment.json")
        self.current_env = None

    def validate(self) -> bool:
        """验证环境配置

        Returns:
            bool: 验证是否通过
        """
        if not self.config_data:
            print("环境配置为空")
            return False

        required_keys = ["env", "base_url", "api_url"]
        for key in required_keys:
            if key not in self.config_data:
                print(f"环境配置缺少必要的键: {key}")
                return False

        self.current_env = self.config_data.get("env")
        if not self.current_env:
            print("当前环境未设置")
            return False

        return True

    def get_base_url(self) -> str:
        """获取基础URL

        Returns:
            str: 基础URL
        """
        if not self.current_env:
            self.current_env = self.config_data.get("env")

        base_urls = self.config_data.get("base_url", {})
        return base_urls.get(self.current_env, "")

    def get_api_url(self) -> str:
        """获取API URL

        Returns:
            str: API URL
        """
        if not self.current_env:
            self.current_env = self.config_data.get("env")

        api_urls = self.config_data.get("api_url", {})
        return api_urls.get(self.current_env, "")

    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置

        Returns:
            Dict[str, Any]: 数据库配置
        """
        if not self.current_env:
            self.current_env = self.config_data.get("env")

        database_configs = self.config_data.get("database", {})
        return database_configs.get(self.current_env, {})

    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置

        Returns:
            Dict[str, Any]: Redis配置
        """
        if not self.current_env:
            self.current_env = self.config_data.get("env")

        redis_configs = self.config_data.get("redis", {})
        return redis_configs.get(self.current_env, {})

    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置

        Returns:
            Dict[str, Any]: 邮件配置
        """
        return self.config_data.get("email", {})

    def set_environment(self, env: str) -> None:
        """设置环境

        Args:
            env: 环境名称
        """
        if env in self.config_data.get("base_url", {}):
            self.config_data["env"] = env
            self.current_env = env
            self.save_config()
        else:
            print(f"不支持的环境: {env}")
