import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader


class TestReportGenerator:
    """测试报告生成器，支持多种格式的报告"""

    def __init__(self, report_dir: Optional[str] = None):
        """初始化报告生成器

        Args:
            report_dir: 报告目录，如果为None则使用默认目录
        """
        # 设置报告目录
        self.report_dir = report_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "reports"
        )
        os.makedirs(self.report_dir, exist_ok=True)

        # 设置模板目录
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates"
        )
        os.makedirs(template_dir, exist_ok=True)

        # 初始化Jinja2环境
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # 创建默认HTML模板
        self._create_default_template()

    def _create_default_template(self):
        """创建默认HTML报告模板"""
        template_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "templates"
        )
        template_path = os.path.join(template_dir, "report_template.html")

        # 如果模板不存在，则创建默认模板
        if not os.path.exists(template_path):
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report_name }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .header {
            background-color: #f5f5f5;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .summary {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
        }
        .summary-item {
            flex: 1;
            padding: 15px;
            text-align: center;
            border-radius: 5px;
            margin: 0 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .summary-item.total {
            background-color: #e3f2fd;
        }
        .summary-item.pass {
            background-color: #e8f5e9;
        }
        .summary-item.fail {
            background-color: #ffebee;
        }
        .test-case {
            margin-bottom: 20px;
            padding: 15px;
            border: 1px solid #eee;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .test-case.pass {
            border-left: 4px solid #4caf50;
        }
        .test-case.fail {
            border-left: 4px solid #f44336;
        }
        .test-case h3 {
            margin-top: 0;
        }
        .test-info {
            margin-bottom: 10px;
            color: #666;
        }
        .test-steps {
            margin-top: 15px;
        }
        .test-step {
            margin-bottom: 5px;
            padding: 5px 10px;
            background-color: #f9f9f9;
            border-radius: 3px;
        }
        .attachments {
            margin-top: 15px;
        }
        .attachment {
            display: inline-block;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .attachment a {
            display: block;
            padding: 5px 10px;
            background-color: #e3f2fd;
            color: #1976d2;
            text-decoration: none;
            border-radius: 3px;
        }
        .attachment a:hover {
            background-color: #bbdefb;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_name }}</h1>
        <p>生成时间: {{ generation_time }}</p>
    </div>

    <div class="summary">
        <div class="summary-item total">
            <h2>{{ test_results|length }}</h2>
            <p>总测试数</p>
        </div>
        <div class="summary-item pass">
            <h2>{{ test_results|selectattr('status', 'equalto', 'PASS')|list|length }}</h2>
            <p>通过数</p>
        </div>
        <div class="summary-item fail">
            <h2>{{ test_results|selectattr('status', 'equalto', 'FAIL')|list|length }}</h2>
            <p>失败数</p>
        </div>
        <div class="summary-item total">
            <h2>{{ (test_results|selectattr('status', 'equalto', 'PASS')|list|length / test_results|length * 100)|round(2) }}%</h2>
            <p>通过率</p>
        </div>
    </div>

    <h2>测试详情</h2>
    {% for test in test_results %}
    <div class="test-case {{ test.status|lower }}">
        <h3>{{ test.test_name }}</h3>
        <div class="test-info">
            <p><strong>状态:</strong> {{ test.status }}</p>
            <p><strong>开始时间:</strong> {{ test.start_time }}</p>
            <p><strong>结束时间:</strong> {{ test.end_time }}</p>
            <p><strong>持续时间:</strong> {{ test.duration }} 秒</p>
            {% if test.message %}
            <p><strong>消息:</strong> {{ test.message }}</p>
            {% endif %}
        </div>

        {% if test.steps %}
        <div class="test-steps">
            <h4>测试步骤:</h4>
            {% for step in test.steps %}
            <div class="test-step">{{ step }}</div>
            {% endfor %}
        </div>
        {% endif %}

        {% if test.attachments %}
        <div class="attachments">
            <h4>附件:</h4>
            {% for attachment in test.attachments %}
            <div class="attachment">
                <a href="{{ attachment.url }}" target="_blank">{{ attachment.name }}</a>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>""")

    def generate_html_report(self, test_results: List[Dict[str, Any]], report_name: Optional[str] = None) -> str:
        """生成HTML报告

        Args:
            test_results: 测试结果列表
            report_name: 报告名称，如果为None则使用默认名称

        Returns:
            str: 报告文件路径
        """
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"test_report_{timestamp}"

        # 如果没有.html后缀，则添加
        if not report_name.endswith(".html"):
            report_name += ".html"

        # 加载模板
        template = self.env.get_template("report_template.html")

        # 渲染模板
        html_content = template.render(
            report_name=report_name,
            generation_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            test_results=test_results
        )

        # 保存报告
        report_path = os.path.join(self.report_dir, report_name)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"HTML报告已生成: {report_path}")
        return report_path

    def generate_json_report(self, test_results: List[Dict[str, Any]], report_name: Optional[str] = None) -> str:
        """生成JSON报告

        Args:
            test_results: 测试结果列表
            report_name: 报告名称，如果为None则使用默认名称

        Returns:
            str: 报告文件路径
        """
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"test_report_{timestamp}"

        # 如果没有.json后缀，则添加
        if not report_name.endswith(".json"):
            report_name += ".json"

        # 准备报告数据
        report_data = {
            "report_name": report_name,
            "generation_time": datetime.now().isoformat(),
            "test_results": test_results
        }

        # 保存报告
        report_path = os.path.join(self.report_dir, report_name)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        print(f"JSON报告已生成: {report_path}")
        return report_path

    def generate_allure_report(self, test_results: List[Dict[str, Any]], report_dir: Optional[str] = None) -> str:
        """生成Allure报告

        Args:
            test_results: 测试结果列表
            report_dir: 报告目录，如果为None则使用默认目录

        Returns:
            str: 报告目录路径
        """
        # 注意：这里只是生成Allure所需的JSON文件，实际生成报告需要使用Allure命令行工具
        if not report_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = os.path.join(self.report_dir, f"allure_{timestamp}")

        os.makedirs(report_dir, exist_ok=True)

        # 为每个测试结果生成Allure JSON文件
        for i, test_result in enumerate(test_results):
            # 准备Allure JSON数据
            allure_data = {
                "name": test_result.get("test_name", f"Test {i + 1}"),
                "status": test_result.get("status", "broken").lower(),
                "statusDetails": {
                    "message": test_result.get("message", "")
                },
                "stage": "finished",
                "steps": [
                    {
                        "name": step,
                        "status": "passed",
                        "stage": "finished",
                        "start": int(time.time() * 1000),
                        "stop": int(time.time() * 1000) + 1
                    }
                    for step in test_result.get("steps", [])
                ],
                "attachments": [
                    {
                        "name": attachment.get("name", "Attachment"),
                        "source": attachment.get("url", ""),
                        "type": "image/png" if attachment.get("url", "").endswith(".png") else "text/plain"
                    }
                    for attachment in test_result.get("attachments", [])
                ],
                "parameters": [],
                "start": int(datetime.strptime(test_result.get("start_time", "2023-01-01 00:00:00"),
                                               "%Y-%m-%d %H:%M:%S").timestamp() * 1000),
                "stop": int(datetime.strptime(test_result.get("end_time", "2023-01-01 00:00:00"),
                                              "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
            }

            # 保存Allure JSON文件
            allure_file = os.path.join(report_dir, f"test_result_{i + 1}.json")
            with open(allure_file, 'w', encoding='utf-8') as f:
                json.dump(allure_data, f, indent=4)

        print(f"Allure报告数据已生成: {report_dir}")
        print("使用以下命令生成Allure报告:")
        print(f"allure generate {report_dir} -o {report_dir}_html --clean")

        return report_dir
