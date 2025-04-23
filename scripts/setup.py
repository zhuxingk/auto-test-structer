import os
import sys
import argparse
import json
import platform
import subprocess
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_arguments():
    """解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="环境设置脚本")
    parser.add_argument("--env", choices=["dev", "test", "prod"], default="dev",
                        help="要设置的环境: dev, test, prod")
    parser.add_argument("--install-drivers", action="store_true",
                        help="是否安装WebDriver驱动")
    parser.add_argument("--create-dirs", action="store_true",
                        help="是否创建必要的目录")

    return parser.parse_args()


def set_environment(env: str):
    """设置环境

    Args:
        env: 环境名称
    """
    print(f"设置环境: {env}")

    # 加载环境配置文件
    config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    env_config_path = os.path.join(config_dir, "environment.json")

    if os.path.exists(env_config_path):
        with open(env_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 更新环境
        config["env"] = env

        # 保存配置
        with open(env_config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)

        print(f"环境已设置为: {env}")
    else:
        print(f"环境配置文件不存在: {env_config_path}")


def install_drivers():
    """安装WebDriver驱动"""
    print("安装WebDriver驱动...")

    # 创建驱动目录
    drivers_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drivers")
    os.makedirs(drivers_dir, exist_ok=True)

    # 安装Chrome驱动
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_driver_path = ChromeDriverManager().install()
        print(f"Chrome驱动已安装: {chrome_driver_path}")
    except Exception as e:
        print(f"安装Chrome驱动失败: {str(e)}")

    # 安装Firefox驱动
    try:
        from webdriver_manager.firefox import GeckoDriverManager
        firefox_driver_path = GeckoDriverManager().install()
        print(f"Firefox驱动已安装: {firefox_driver_path}")
    except Exception as e:
        print(f"安装Firefox驱动失败: {str(e)}")

    # 安装Edge驱动
    try:
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        edge_driver_path = EdgeChromiumDriverManager().install()
        print(f"Edge驱动已安装: {edge_driver_path}")
    except Exception as e:
        print(f"安装Edge驱动失败: {str(e)}")


def create_directories():
    """创建必要的目录"""
    print("创建必要的目录...")

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 需要创建的目录
    dirs = [
        os.path.join(root_dir, "logs"),
        os.path.join(root_dir, "reports"),
        os.path.join(root_dir, "screenshots", "web"),
        os.path.join(root_dir, "screenshots", "mobile"),
        os.path.join(root_dir, "data"),
        os.path.join(root_dir, "templates"),
        os.path.join(root_dir, "drivers"),
        os.path.join(root_dir, "downloads")
    ]

    # 创建目录
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"目录已创建: {directory}")


def main():
    """主函数"""
    args = parse_arguments()

    # 设置环境
    set_environment(args.env)

    # 安装驱动
    if args.install_drivers:
        install_drivers()

    # 创建目录
    if args.create_dirs:
        create_directories()

    print("环境设置完成")


if __name__ == "__main__":
    main()
