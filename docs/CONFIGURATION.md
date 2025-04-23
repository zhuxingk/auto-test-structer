# 配置说明

## 配置管理概述

本项目使用统一的配置管理系统，支持多种配置类型和环境。配置系统基于JSON格式，提供了灵活的配置管理和验证机制。

## 配置类结构

### 1. 基础配置类 (BaseConfig)
```python
class BaseConfig:
    """基础配置类，提供通用的配置管理功能"""
    
    def load_config(self) -> bool:
        """加载配置文件"""
        
    def save_config(self) -> bool:
        """保存配置文件"""
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        
    def update(self, config_dict: Dict[str, Any]) -> None:
        """更新配置"""
        
    def validate(self) -> bool:
        """验证配置"""
```

### 2. 环境配置类 (EnvironmentConfig)
```python
class EnvironmentConfig(BaseConfig):
    """环境配置类，管理不同环境的配置"""
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        
    def get_api_url(self) -> str:
        """获取API URL"""
        
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        
    def get_redis_config(self) -> Dict[str, Any]:
        """获取Redis配置"""
        
    def get_email_config(self) -> Dict[str, Any]:
        """获取邮件配置"""
        
    def set_environment(self, env: str) -> None:
        """设置环境"""
```

### 3. 测试配置类 (TestConfig)
```python
class TestConfig(BaseConfig):
    """测试配置类，管理测试相关的配置"""
    
    def get_web_config(self) -> Dict[str, Any]:
        """获取Web测试配置"""
        
    def get_api_config(self) -> Dict[str, Any]:
        """获取API测试配置"""
        
    def get_mobile_config(self) -> Dict[str, Any]:
        """获取移动端测试配置"""
        
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能测试配置"""
        
    def get_concurrency_config(self) -> Dict[str, Any]:
        """获取并发测试配置"""
        
    def get_report_config(self) -> Dict[str, Any]:
        """获取报告配置"""
        
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
```

### 4. 工具配置类 (ToolConfig)
```python
class ToolConfig(BaseConfig):
    """工具配置类，管理各种工具的配置"""
    
    def get_selenium_config(self) -> Dict[str, Any]:
        """获取Selenium配置"""
        
    def get_appium_config(self) -> Dict[str, Any]:
        """获取Appium配置"""
        
    def get_jmeter_config(self) -> Dict[str, Any]:
        """获取JMeter配置"""
        
    def get_postman_config(self) -> Dict[str, Any]:
        """获取Postman配置"""
        
    def get_git_config(self) -> Dict[str, Any]:
        """获取Git配置"""
        
    def get_jenkins_config(self) -> Dict[str, Any]:
        """获取Jenkins配置"""
        
    def get_docker_config(self) -> Dict[str, Any]:
        """获取Docker配置"""
```

## 配置文件结构

### 1. 环境配置文件 (environment.json)
```json
{
    "env": "dev",
    "base_url": {
        "dev": "http://dev.example.com",
        "test": "http://test.example.com",
        "prod": "http://example.com"
    },
    "api_url": {
        "dev": "http://api.dev.example.com",
        "test": "http://api.test.example.com",
        "prod": "http://api.example.com"
    },
    "database": {
        "dev": {
            "host": "localhost",
            "port": 3306,
            "user": "dev_user",
            "password": "dev_password",
            "database": "dev_db"
        }
    },
    "redis": {
        "dev": {
            "host": "localhost",
            "port": 6379,
            "password": "dev_password",
            "db": 0
        }
    },
    "email": {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "test@example.com",
        "password": "email_password",
        "from_address": "test@example.com",
        "to_addresses": ["admin@example.com"]
    }
}
```

### 2. 测试配置文件 (test.json)
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
    },
    "api": {
        "timeout": 30,
        "verify_ssl": true,
        "retry_times": 3,
        "retry_interval": 1,
        "log_response": true,
        "log_headers": false
    },
    "mobile": {
        "platform": "android",
        "device_name": "emulator-5554",
        "app_package": "com.example.app",
        "app_activity": "com.example.app.MainActivity",
        "app_path": "apps/example.apk",
        "implicit_wait": 10,
        "screenshot_dir": "screenshots/mobile"
    },
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
    },
    "concurrency": {
        "max_threads": 10,
        "max_iterations": 100,
        "thread_delay": 1.0,
        "timeout": 300
    },
    "report": {
        "types": ["html", "allure", "json"],
        "output_dir": "reports",
        "template_dir": "templates",
        "retention_days": 7
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/test.log",
        "max_size": 10485760,
        "backup_count": 5
    }
}
```

### 3. 工具配置文件 (tool.json)
```json
{
    "selenium": {
        "webdriver_path": "drivers",
        "chrome_driver": "chromedriver.exe",
        "firefox_driver": "geckodriver.exe",
        "edge_driver": "msedgedriver.exe",
        "download_dir": "downloads",
        "proxy": {
            "enabled": false,
            "host": "localhost",
            "port": 8080
        }
    },
    "appium": {
        "server_url": "http://localhost:4723",
        "desired_capabilities": {
            "platformName": "Android",
            "platformVersion": "11.0",
            "deviceName": "emulator-5554",
            "automationName": "UiAutomator2",
            "appPackage": "com.example.app",
            "appActivity": "com.example.app.MainActivity"
        },
        "app_path": "apps/example.apk",
        "screenshot_dir": "screenshots/mobile"
    },
    "jmeter": {
        "path": "tools/apache-jmeter",
        "test_plan_dir": "test_plans",
        "result_dir": "results",
        "report_dir": "reports/jmeter",
        "properties": {
            "jmeter.save.saveservice.output_format": "xml",
            "jmeter.save.saveservice.response_data": "true",
            "jmeter.save.saveservice.samplerData": "true"
        }
    },
    "postman": {
        "collection_dir": "collections",
        "environment_dir": "environments",
        "data_dir": "data",
        "report_dir": "reports/postman"
    },
    "git": {
        "repository": "https://github.com/example/repo.git",
        "branch": "main",
        "username": "user",
        "email": "user@example.com",
        "token": ""
    },
    "jenkins": {
        "url": "http://localhost:8080",
        "username": "admin",
        "token": "",
        "job_name": "test-automation",
        "build_parameters": {
            "environment": "test",
            "browser": "chrome"
        }
    },
    "docker": {
        "registry": "docker.io",
        "username": "user",
        "password": "",
        "image_prefix": "test-automation",
        "compose_file": "docker-compose.yml"
    }
}
```

## 配置使用指南

### 1. 加载配置
```python
from config import EnvironmentConfig, TestConfig, ToolConfig

# 加载环境配置
env_config = EnvironmentConfig()
env_config.load_config()

# 加载测试配置
test_config = TestConfig()
test_config.load_config()

# 加载工具配置
tool_config = ToolConfig()
tool_config.load_config()
```

### 2. 获取配置
```python
# 获取环境配置
base_url = env_config.get_base_url()
db_config = env_config.get_database_config()

# 获取测试配置
web_config = test_config.get_web_config()
api_config = test_config.get_api_config()

# 获取工具配置
selenium_config = tool_config.get_selenium_config()
appium_config = tool_config.get_appium_config()
```

### 3. 更新配置
```python
# 更新环境
env_config.set_environment("test")

# 更新配置项
test_config.set("web.browser", "firefox")
tool_config.set("selenium.headless", True)

# 批量更新
new_config = {
    "web": {
        "browser": "chrome",
        "headless": True
    }
}
test_config.update(new_config)
```

### 4. 验证配置
```python
# 验证配置
if not env_config.validate():
    print("环境配置验证失败")
    
if not test_config.validate():
    print("测试配置验证失败")
    
if not tool_config.validate():
    print("工具配置验证失败")
```

## 配置最佳实践

### 1. 环境管理
- 为不同环境维护独立的配置文件
- 使用环境变量管理敏感信息
- 定期备份配置文件
- 版本控制配置文件

### 2. 配置验证
- 实现完整的配置验证
- 提供详细的错误信息
- 设置合理的默认值
- 定期检查配置有效性

### 3. 安全性
- 加密敏感信息
- 限制配置文件权限
- 使用环境变量存储密钥
- 定期轮换凭证

### 4. 维护性
- 保持配置结构清晰
- 添加必要的注释
- 定期清理过期配置
- 记录配置变更历史 