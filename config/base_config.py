import json
import os
from typing import Any, Dict


class BaseConfig:
    """基础配置类，提供通用的配置管理功能"""

    def __init__(self, config_file_name=None):
        """初始化配置类

        Args:
            config_file_name: 配置文件名称
        """
        self.config_file_name = config_file_name
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.config_data = {}

    def load_config(self) -> bool:
        """加载配置文件

        Returns:
            bool: 加载是否成功
        """
        if not self.config_file_name:
            return False

        config_path = os.path.join(self.config_dir, self.config_file_name)

        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return False

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            return True
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return False

    def save_config(self) -> bool:
        """保存配置文件

        Returns:
            bool: 保存是否成功
        """
        if not self.config_file_name:
            return False

        config_path = os.path.join(self.config_dir, self.config_file_name)

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项

        Args:
            key: 配置键，支持点号分隔的多级键
            default: 默认值

        Returns:
            Any: 配置值
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """设置配置项

        Args:
            key: 配置键，支持点号分隔的多级键
            value: 配置值
        """
        keys = key.split('.')
        data = self.config_data

        for i, k in enumerate(keys[:-1]):
            if k not in data:
                data[k] = {}
            data = data[k]

        data[keys[-1]] = value

    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新配置

        Args:
            config_dict: 配置字典
        """

        def update_dict(source, updates):
            for key, value in updates.items():
                if key in source and isinstance(source[key], dict) and isinstance(value, dict):
                    update_dict(source[key], value)
                else:
                    source[key] = value

        update_dict(self.config_data, config_dict)

    def validate(self) -> bool:
        """验证配置

        Returns:
            bool: 验证是否通过
        """
        # 基类中的验证逻辑可以根据需要扩展
        return True
