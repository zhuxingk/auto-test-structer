import os
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testcases.example_test import WebLoginTest, ApiUserTest
from testcases.report_generator import TestReportGenerator


def parse_arguments():
    """解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="自动化测试执行脚本")
    parser.add_argument("--test-type", choices=["web", "api", "mobile", "all"], default="all",
                        help="要执行的测试类型: web, api, mobile, all")
    parser.add_argument("--report-type", choices=["html", "json", "allure", "all"], default="html",
                        help="要生成的报告类型: html, json, allure, all")
    parser.add_argument("--report-name", help="报告名称")
    parser.add_argument("--headless", action="store_true", help="是否以无头模式运行Web测试")

    return parser.parse_args()


def run_web_tests(headless: bool = False) -> List[Dict[str, Any]]:
    """运行Web测试

    Args:
        headless: 是否以无头模式运行

    Returns:
        List[Dict[str, Any]]: 测试结果列表
    """
    print("开始执行Web测试...")

    # 在实际项目中，可以动态查找和加载测试用例
    web_tests = [
        WebLoginTest()
    ]

    results = []
    for test in web_tests:
        print(f"执行测试: {test.test_name}")
        result = test.run()
        results.append(result)

    print("Web测试执行完成")
    return results


def run_api_tests() -> List[Dict[str, Any]]:
    """运行API测试

    Returns:
        List[Dict[str, Any]]: 测试结果列表
    """
    print("开始执行API测试...")

    # 在实际项目中，可以动态查找和加载测试用例
    api_tests = [
        ApiUserTest()
    ]

    results = []
    for test in api_tests:
        print(f"执行测试: {test.test_name}")
        result = test.run()
        results.append(result)

    print("API测试执行完成")
    return results


def run_mobile_tests() -> List[Dict[str, Any]]:
    """运行移动端测试

    Returns:
        List[Dict[str, Any]]: 测试结果列表
    """
    print("开始执行移动端测试...")
    print("注意: 移动端测试尚未实现")
    return []


def generate_reports(test_results: List[Dict[str, Any]], report_types: List[str], report_name: str = None):
    """生成测试报告

    Args:
        test_results: 测试结果列表
        report_types: 报告类型列表
        report_name: 报告名称
    """
    if not test_results:
        print("没有测试结果，无法生成报告")
        return

    # 如果没有指定报告名称，则使用时间戳
    if not report_name:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"test_report_{timestamp}"

    # 创建报告生成器
    generator = TestReportGenerator()

    # 生成报告
    for report_type in report_types:
        if report_type == "html":
            generator.generate_html_report(test_results, f"{report_name}.html")
        elif report_type == "json":
            generator.generate_json_report(test_results, f"{report_name}.json")
        elif report_type == "allure":
            generator.generate_allure_report(test_results)


def main():
    """主函数"""
    args = parse_arguments()

    # 确定要执行的测试类型
    test_types = ["web", "api", "mobile"] if args.test_type == "all" else [args.test_type]

    # 确定要生成的报告类型
    report_types = ["html", "json", "allure"] if args.report_type == "all" else [args.report_type]

    # 运行测试
    all_results = []

    if "web" in test_types:
        web_results = run_web_tests(args.headless)
        all_results.extend(web_results)

    if "api" in test_types:
        api_results = run_api_tests()
        all_results.extend(api_results)

    if "mobile" in test_types:
        mobile_results = run_mobile_tests()
        all_results.extend(mobile_results)

    # 生成报告
    generate_reports(all_results, report_types, args.report_name)


if __name__ == "__main__":
    main()
