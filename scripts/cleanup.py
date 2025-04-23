import os
import sys
import argparse
import shutil
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def parse_arguments():
    """解析命令行参数

    Returns:
        argparse.Namespace: 解析后的参数
    """
    parser = argparse.ArgumentParser(description="清理脚本，用于清理测试产生的临时文件和报告")
    parser.add_argument("--all", action="store_true", help="清理所有文件")
    parser.add_argument("--logs", action="store_true", help="清理日志文件")
    parser.add_argument("--reports", action="store_true", help="清理报告文件")
    parser.add_argument("--screenshots", action="store_true", help="清理截图文件")
    parser.add_argument("--downloads", action="store_true", help="清理下载文件")
    parser.add_argument("--days", type=int, default=7, help="清理N天前的文件，默认为7天")
    parser.add_argument("--dry-run", action="store_true", help="仅显示将被删除的文件，不实际删除")

    return parser.parse_args()


def get_files_older_than(directory, days):
    """获取指定目录下早于指定天数的文件

    Args:
        directory: 目录路径
        days: 天数

    Returns:
        list: 文件路径列表
    """
    if not os.path.exists(directory):
        return []

    cutoff_date = datetime.now() - timedelta(days=days)
    old_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))

            if file_mtime < cutoff_date:
                old_files.append(file_path)

    return old_files


def cleanup_directory(directory, days, dry_run=False):
    """清理指定目录下早于指定天数的文件

    Args:
        directory: 目录路径
        days: 天数
        dry_run: 是否仅显示将被删除的文件，不实际删除

    Returns:
        int: 删除的文件数量
    """
    if not os.path.exists(directory):
        print(f"目录不存在: {directory}")
        return 0

    old_files = get_files_older_than(directory, days)

    if not old_files:
        print(f"目录 {directory} 中没有早于 {days} 天的文件")
        return 0

    print(f"在目录 {directory} 中找到 {len(old_files)} 个早于 {days} 天的文件")

    if dry_run:
        for file in old_files:
            print(f"将删除: {file}")
        return 0

    deleted_count = 0
    for file in old_files:
        try:
            os.remove(file)
            print(f"已删除: {file}")
            deleted_count += 1
        except Exception as e:
            print(f"删除文件 {file} 失败: {str(e)}")

    return deleted_count


def cleanup_all_directories(directories, days, dry_run=False):
    """清理多个目录下早于指定天数的文件

    Args:
        directories: 目录路径列表
        days: 天数
        dry_run: 是否仅显示将被删除的文件，不实际删除

    Returns:
        int: 删除的文件数量
    """
    total_deleted = 0

    for directory in directories:
        deleted = cleanup_directory(directory, days, dry_run)
        total_deleted += deleted

    return total_deleted


def cleanup_empty_directories(root_dir):
    """递归删除空目录

    Args:
        root_dir: 根目录路径

    Returns:
        int: 删除的目录数量
    """
    if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
        return 0

    deleted_count = 0

    for root, dirs, files in os.walk(root_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)

            if not os.listdir(dir_path):  # 检查目录是否为空
                try:
                    os.rmdir(dir_path)
                    print(f"已删除空目录: {dir_path}")
                    deleted_count += 1
                except Exception as e:
                    print(f"删除目录 {dir_path} 失败: {str(e)}")

    return deleted_count


def main():
    """主函数"""
    args = parse_arguments()

    # 项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 需要清理的目录
    directories = []

    if args.all or args.logs:
        directories.append(os.path.join(root_dir, "logs"))

    if args.all or args.reports:
        directories.append(os.path.join(root_dir, "reports"))

    if args.all or args.screenshots:
        directories.append(os.path.join(root_dir, "screenshots"))

    if args.all or args.downloads:
        directories.append(os.path.join(root_dir, "downloads"))

    if not directories:
        print("未指定要清理的目录，请使用 --all, --logs, --reports, --screenshots 或 --downloads 选项")
        return

    # 清理文件
    total_deleted = cleanup_all_directories(directories, args.days, args.dry_run)

    if args.dry_run:
        print(f"共有 {total_deleted} 个文件将被删除")
    else:
        print(f"共删除了 {total_deleted} 个文件")

        # 清理空目录
        deleted_dirs = 0
        for directory in directories:
            deleted_dirs += cleanup_empty_directories(directory)

        if deleted_dirs > 0:
            print(f"共删除了 {deleted_dirs} 个空目录")


if __name__ == "__main__":
    main()
