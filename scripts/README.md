# 自动化测试框架

## 项目概述

这是一个基于Python的自动化测试框架，支持Web、API和移动端测试。框架提供了灵活的配置管理、测试用例管理和报告生成功能。

## 功能特性

- 支持多环境配置（开发、测试、生产）
- 统一的配置管理接口
- Web自动化测试（基于Selenium）
- API自动化测试（基于Requests）
- 移动端自动化测试（基于Appium）
- 灵活的测试报告生成（HTML、JSON、Allure）
- 测试用例基类，提供通用功能

## 项目结构

project/
├── config/                    # 配置管理目录
│   ├── init.py            # 配置模块初始化
│   ├── base_config.py         # 基础配置类
│   ├── environment_config.py  # 环境配置类
│   ├── test_config.py         # 测试配置类
│   └── tool_config.py         # 工具配置类
├── testcases/                 # 测试用例目录
│   ├── api/                   # API测试用例
│   ├── web/                   # Web测试用例
│   ├── mobile/                # 移动端测试用例
│   ├── common/                # 公共测试用例
│   ├── systems/               # 系统特定测试用例
│   ├── utils/                 # 测试工具类
│   ├── base_test.py           # 测试用例基类
│   ├── report_generator.py    # 报告生成器
│   └── example_test.py        # 测试用例示例
├── scripts/                   # 自动化脚本
│   ├── setup.py               # 环境设置脚本
│   └── run_tests.py           # 测试执行脚本
├── docs/                      # 文档目录
├── data/                      # 测试数据目录
├── reports/                   # 测试报告目录
├── logs/                      # 日志文件目录
├── screenshots/               # 截图保存目录
│   ├── web/                   # Web测试截图
│   └── mobile/                # 移动端测试截图
├── templates/                 # 报告模板目录
├── drivers/                   # WebDriver驱动目录
├── README.md                  # 项目说明
└── requirements.txt           # 项目依赖