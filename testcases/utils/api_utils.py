import os
import json
import time
import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException

from config.test_config import TestConfig
from config.environment_config import EnvironmentConfig


class ApiUtils:
    """API测试工具类，封装HTTP请求操作"""

    def __init__(self):
        """初始化API测试工具类"""
        self.test_config = TestConfig()
        self.test_config.load_config()

        self.env_config = EnvironmentConfig()
        self.env_config.load_config()

        self.api_config = self.test_config.get_api_config()
        self.base_url = self.env_config.get_api_url()

        self.timeout = self.api_config.get("timeout", 30)
        self.verify_ssl = self.api_config.get("verify_ssl", True)
        self.retry_times = self.api_config.get("retry_times", 3)
        self.retry_interval = self.api_config.get("retry_interval", 1)
        self.log_response = self.api_config.get("log_response", True)
        self.log_headers = self.api_config.get("log_headers", False)

        self.headers = {}
        self.session = requests.Session()

    def set_headers(self, headers: Dict[str, str]):
        """设置请求头

        Args:
            headers: 请求头字典
        """
        self.headers.update(headers)

    def get_auth_token(self, username: str, password: str, token_url: Optional[str] = None) -> str:
        """获取认证令牌

        Args:
            username: 用户名
            password: 密码
            token_url: 令牌URL，如果为None则使用默认URL

        Returns:
            str: 认证令牌
        """
        token_url = token_url or f"{self.base_url}/auth/token"

        response = self.send_request(
            "POST",
            token_url,
            json={"username": username, "password": password}
        )

        if response.status_code == 200:
            return response.json().get("token", "")
        else:
            raise Exception(f"获取认证令牌失败: {response.status_code} {response.text}")

    def send_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送HTTP请求

        Args:
            method: 请求方法，如GET, POST等
            url: 请求URL，如果不是完整URL则会添加base_url前缀
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        # 处理URL
        if not url.startswith(("http://", "https://")):
            url = f"{self.base_url}{url}"

        # 处理请求头
        headers = kwargs.pop("headers", {})
        headers.update(self.headers)

        # 处理超时和SSL验证
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify_ssl)

        # 记录请求信息
        print(f"发送请求: {method} {url}")
        if self.log_headers and headers:
            print(f"请求头: {json.dumps(headers, indent=2)}")

        # 发送请求，支持重试
        for i in range(self.retry_times + 1):
            try:
                response = self.session.request(method, url, headers=headers, **kwargs)

                # 记录响应信息
                print(f"响应状态码: {response.status_code}")
                if self.log_headers:
                    print(f"响应头: {json.dumps(dict(response.headers), indent=2)}")
                if self.log_response:
                    try:
                        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
                    except:
                        print(f"响应内容: {response.text[:500]}...")

                return response
            except RequestException as e:
                if i < self.retry_times:
                    print(f"请求失败，重试 {i + 1}/{self.retry_times}: {str(e)}")
                    time.sleep(self.retry_interval)
                else:
                    raise

    def get(self, url: str, **kwargs) -> requests.Response:
        """发送GET请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        return self.send_request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """发送POST请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        return self.send_request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> requests.Response:
        """发送PUT请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        return self.send_request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs) -> requests.Response:
        """发送DELETE请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        return self.send_request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs) -> requests.Response:
        """发送PATCH请求

        Args:
            url: 请求URL
            **kwargs: 其他请求参数

        Returns:
            Response: 响应对象
        """
        return self.send_request("PATCH", url, **kwargs)

    def validate_response(self, response: requests.Response, expected_status_code: int = 200) -> bool:
        """验证响应

        Args:
            response: 响应对象
            expected_status_code: 预期状态码

        Returns:
            bool: 验证是否通过
        """
        return response.status_code == expected_status_code

    def cleanup(self):
        """清理资源"""
        self.session.close()
