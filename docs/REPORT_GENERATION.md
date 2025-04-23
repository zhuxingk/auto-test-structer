# 报告生成说明文档

## 目录
1. [报告生成器概述](#报告生成器概述)
2. [HTML报告](#html报告)
3. [JSON报告](#json报告)
4. [Allure报告](#allure报告)
5. [自定义报告模板](#自定义报告模板)
6. [报告发送](#报告发送)

## 报告生成器概述

报告生成器位于 `testcases/report_generator.py`，支持多种格式的测试报告生成：

```python
class TestReportGenerator:
    def __init__(self, report_dir: str = None):
        self.report_dir = report_dir or os.path.join(os.path.dirname(__file__), "reports")
        self.env = Environment(loader=FileSystemLoader("templates"))
    
    def generate_html_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        pass
    
    def generate_json_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
        pass
    
    def generate_allure_report(self, test_results: List[Dict[str, Any]], report_dir: str = None) -> str:
        pass
```

## HTML报告

### 基本使用
```python
from testcases.report_generator import TestReportGenerator

# 准备测试结果
test_results = [
    {
        "test_name": "test_1",
        "status": "PASS",
        "start_time": "2024-01-01 10:00:00",
        "end_time": "2024-01-01 10:01:00",
        "duration": 60,
        "steps": ["步骤1", "步骤2"],
        "attachments": [{"name": "截图1", "url": "screenshots/test_1.png"}]
    }
]

# 生成HTML报告
generator = TestReportGenerator()
report_path = generator.generate_html_report(test_results)
```

### 报告内容
- 测试统计信息
  - 总测试数
  - 通过数
  - 失败数
  - 通过率
- 测试详情
  - 测试名称
  - 测试状态
  - 开始时间
  - 结束时间
  - 持续时间
  - 测试步骤
  - 附件

### 自定义样式
可以通过修改 `templates/report_template.html` 中的 CSS 样式来自定义报告外观：

```html
<style>
    /* 自定义样式 */
    .test-case {
        margin-bottom: 20px;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 5px;
    }
    
    .test-case.pass {
        border-left: 4px solid #28a745;
    }
    
    .test-case.fail {
        border-left: 4px solid #dc3545;
    }
</style>
```

## JSON报告

### 基本使用
```python
from testcases.report_generator import TestReportGenerator

# 生成JSON报告
generator = TestReportGenerator()
report_path = generator.generate_json_report(test_results)
```

### 报告格式
```json
{
    "report_name": "test_report_20240101_100000.json",
    "generation_time": "2024-01-01T10:00:00",
    "test_results": [
        {
            "test_name": "test_1",
            "status": "PASS",
            "start_time": "2024-01-01 10:00:00",
            "end_time": "2024-01-01 10:01:00",
            "duration": 60,
            "steps": ["步骤1", "步骤2"],
            "attachments": [{"name": "截图1", "url": "screenshots/test_1.png"}]
        }
    ]
}
```

### 使用场景
- 自动化处理测试结果
- 集成到其他系统
- 数据分析和统计

## Allure报告

### 基本使用
```python
from testcases.report_generator import TestReportGenerator

# 生成Allure报告
generator = TestReportGenerator()
report_dir = generator.generate_allure_report(test_results)
```

### 报告结构
```
allure_report_20240101_100000/
├── test_1-result.json
├── test_2-result.json
└── ...
```

### 报告内容
- 测试用例名称
- 测试状态
- 开始时间
- 结束时间
- 测试步骤
- 附件

### 使用场景
- 与Allure报告系统集成
- 生成更详细的测试报告
- 支持测试趋势分析

## 自定义报告模板

### 创建新模板
1. 在 `templates` 目录下创建新的模板文件，例如 `custom_report.html`
2. 使用Jinja2模板语法定义报告结构
3. 在报告生成器中添加新的生成方法

### 模板示例
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ report_name }}</title>
    <style>
        /* 自定义样式 */
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ report_name }}</h1>
        <div class="stats">
            <!-- 统计信息 -->
        </div>
        <div class="test-results">
            {% for result in test_results %}
            <div class="test-case">
                <!-- 测试结果详情 -->
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
```

### 使用新模板
```python
def generate_custom_report(self, test_results: List[Dict[str, Any]], report_name: str = None) -> str:
    template = self.env.get_template("custom_report.html")
    # 生成报告
    return report_path
```

## 报告发送

### 邮件发送
```python
def send_report_by_email(self, report_path: str, recipients: List[str] = None):
    email_config = TestConfig.get_config("email")
    recipients = recipients or email_config["recipients"]
    
    # 准备邮件内容
    msg = MIMEMultipart()
    msg["Subject"] = f"{email_config['subject_prefix']} 测试报告"
    msg["From"] = email_config["username"]
    msg["To"] = ", ".join(recipients)
    
    # 添加报告附件
    with open(report_path, "rb") as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(report_path)
        )
        msg.attach(attachment)
    
    # 发送邮件
    with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
        server.starttls()
        server.login(email_config["username"], email_config["password"])
        server.send_message(msg)
```

### 其他发送方式
- 上传到文件服务器
- 发送到消息队列
- 集成到CI/CD系统

## 最佳实践

### 1. 报告生成
- 定期清理过期报告
- 使用有意义的报告名称
- 包含必要的测试信息
- 优化报告性能

### 2. 报告存储
- 使用版本控制
- 定期备份
- 设置访问权限
- 管理存储空间

### 3. 报告分发
- 选择合适的发送方式
- 控制发送频率
- 管理接收人列表
- 处理发送失败

### 4. 报告分析
- 提取关键指标
- 生成趋势图表
- 识别问题模式
- 提供改进建议 