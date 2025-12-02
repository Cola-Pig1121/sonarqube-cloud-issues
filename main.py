#!/usr/bin/env python3
"""
SonarCloud Issues
Usage: uv run main.py
"""

import base64
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime

import pandas as pd
import requests

# ==================== 配置文件路径 ====================
CONFIG_FILE = ".sonarcloud_config.json"
# API端点
API_URL = "https://sonarcloud.io/api/issues/search"
# 输出文件名前缀
OUTPUT_PREFIX = "sonarcloud_issues"
# 当前版本
CURRENT_VERSION = "0.1.0"
# GitHub API URL
GITHUB_API_URL = (
    "https://api.github.com/repos/Cola-Pig1121/sonarqube-cloud-issues/releases/latest"
)
# 更新URL模板
UPDATE_BASE_URL = (
    "https://github.com/Cola-Pig1121/sonarqube-cloud-issues/releases/download/{version}"
)
# ====================================================


def load_config():
    """从配置文件加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # 确保新字段存在
                if "branch" not in config:
                    config["branch"] = "main"
                if "pr_number" not in config:
                    config["pr_number"] = ""
                return config
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return None
    return None


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("配置已保存")
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


def prompt_for_config():
    """交互式配置设置"""
    print("\n" + "=" * 60)
    print("SonarCloud 配置设置")
    print("=" * 60)
    print("提示：按 Ctrl+C 可取消配置")
    print("-" * 60)

    try:
        print("错误：请设置SONAR_TOKEN为你的User Token")
        print("   获取方式：SonarCloud → My Account → Security → Generate Token")
        token = input("1. 请输入SonarCloud User Token: ").strip()
        if not token:
            print("错误：Token不能为空")
            return None

        print("错误：请设置PROJECT_KEY和ORGANIZATION")
        print("   示例：PROJECT_KEY='org_pro'，ORGANIZATION='org'")
        project_key = input("2. 请输入Project Key: ").strip()
        if not project_key:
            print("错误：Project Key不能为空")
            return None

        organization = input("3. 请输入Organization Key（小写）: ").strip().lower()
        if not organization:
            print("错误：Organization Key不能为空")
            return None

        print("提示：默认分支通常为 main 或 master")
        branch = input("4. 请输入默认分支名称 [main]: ").strip()
        if not branch:
            branch = "main"

        print("提示：如需导出PR，请填写PR编号，否则留空")
        pr_number = input("5. 请输入默认PR编号（留空表示不导出PR）: ").strip()

        config = {
            "sonar_token": token,
            "project_key": project_key,
            "organization": organization,
            "branch": branch,
            "pr_number": pr_number,
            "created_at": datetime.now().isoformat(),
        }

        return config
    except KeyboardInterrupt:
        print("\n取消配置")
        return None


def set_branch():
    """单独设置分支"""
    config = load_config() or {}
    try:
        print("提示：默认分支通常为 main 或 master")
        branch = input("请输入分支名称 [main]: ").strip()
        if not branch:
            branch = "main"
        config["branch"] = branch
        config["updated_at"] = datetime.now().isoformat()
        save_config(config)
    except KeyboardInterrupt:
        print("\n取消操作")


def set_pr_number():
    """单独设置PR编号"""
    config = load_config() or {}
    try:
        print("提示：留空表示不导出PR")
        pr_number = input("请输入默认PR编号（留空清除）: ").strip()
        config["pr_number"] = pr_number
        config["updated_at"] = datetime.now().isoformat()
        save_config(config)
    except KeyboardInterrupt:
        print("\n取消操作")


def show_settings_menu():
    """显示设置菜单"""
    while True:
        print("\n" + "=" * 60)
        print("设置菜单")
        print("=" * 60)
        print("(1) 配置SonarCloud Token")
        print("(2) 配置Project Key")
        print("(3) 配置Organization Key")
        print("(4) 配置默认分支")
        print("(5) 配置默认PR编号")
        print("(6) 查看当前配置")
        print("(7) 重新配置所有设置")
        print("(8) 检查更新")
        print("(0) 返回主菜单")
        print("=" * 60)

        choice = input("请选择: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            set_token()
        elif choice == "2":
            set_project_key()
        elif choice == "3":
            set_organization()
        elif choice == "4":
            set_branch()
        elif choice == "5":
            set_pr_number()
        elif choice == "6":
            view_config()
        elif choice == "7":
            reconfigure_all()
        elif choice == "8":
            check_for_updates()
        else:
            print("无效选项")


def set_token():
    """单独设置Token"""
    config = load_config() or {}
    try:
        print("错误：请设置SONAR_TOKEN为你的User Token")
        print("   获取方式：SonarCloud → My Account → Security → Generate Token")
        token = input("请输入新的User Token: ").strip()
        if token:
            config["sonar_token"] = token
            config["updated_at"] = datetime.now().isoformat()
            save_config(config)
        else:
            print("Token不能为空")
    except KeyboardInterrupt:
        print("\n取消操作")


def set_project_key():
    """单独设置Project Key"""
    config = load_config() or {}
    try:
        print("错误：请设置PROJECT_KEY和ORGANIZATION")
        print("   示例：PROJECT_KEY='org_pro'，ORGANIZATION='org'")
        project_key = input("请输入新的Project Key: ").strip()
        if project_key:
            config["project_key"] = project_key
            config["updated_at"] = datetime.now().isoformat()
            save_config(config)
        else:
            print("Project Key不能为空")
    except KeyboardInterrupt:
        print("\n取消操作")


def set_organization():
    """单独设置Organization"""
    config = load_config() or {}
    try:
        print("错误：请设置PROJECT_KEY和ORGANIZATION")
        print("   示例：PROJECT_KEY='org_pro'，ORGANIZATION='org'")
        organization = input("请输入新的Organization Key（小写）: ").strip().lower()
        if organization:
            config["organization"] = organization
            config["updated_at"] = datetime.now().isoformat()
            save_config(config)
        else:
            print("Organization Key不能为空")
    except KeyboardInterrupt:
        print("\n取消操作")


def view_config():
    """查看当前配置"""
    config = load_config()
    if not config:
        print("\n当前未配置")
        return

    print("\n" + "=" * 60)
    print("当前配置")
    print("=" * 60)
    token_display = (
        config.get("sonar_token", "")[:8] + "..."
        if config.get("sonar_token")
        else "未设置"
    )
    print(f"Token: {token_display}")
    print(f"Project Key: {config.get('project_key', '未设置')}")
    print(f"Organization: {config.get('organization', '未设置')}")
    print(f"默认分支: {config.get('branch', 'main')}")
    print(f"PR编号: {config.get('pr_number', '未设置')}")
    print(f"创建时间: {config.get('created_at', '未知')}")
    print(f"当前版本: {CURRENT_VERSION}")
    print("=" * 60)


def reconfigure_all():
    """重新配置所有设置"""
    print("\n重新配置所有设置...")
    config = prompt_for_config()
    if config:
        save_config(config)


def get_config_or_prompt():
    """获取配置，如果不存在则提示用户配置"""
    config = load_config()
    if not config:
        print("\n首次运行，需要进行配置")
        config = prompt_for_config()
        if config:
            save_config(config)
        else:
            print("配置失败，程序退出")
            sys.exit(1)
    return config


def select_scope(config):
    """选择导出范围（分支/PR）"""
    print("\n" + "=" * 60)
    print("选择导出范围")
    print("=" * 60)
    print(f"(1) 默认分支: {config.get('branch', 'main')}")
    print("(2) 指定分支")
    print("(3) Pull Request")
    print("(4) 所有分支汇总")
    print("(0) 返回主菜单")
    print("=" * 60)

    choice = input("请选择: ").strip()

    if choice == "0":
        return None, None
    elif choice == "1":
        return config.get("branch", "main"), None
    elif choice == "2":
        branch = input("请输入分支名称: ").strip()
        if not branch:
            print("错误：分支名称不能为空")
            return None, None
        return branch, None
    elif choice == "3":
        pr_number = input("请输入PR编号: ").strip()
        if not pr_number:
            print("错误：PR编号不能为空")
            return None, None
        return None, pr_number
    elif choice == "4":
        return None, None  # 不传branch参数表示汇总
    else:
        print("无效选项")
        return None, None


def select_severity_levels():
    """选择要导出的Issues严重级别"""
    print("\n" + "=" * 60)
    print("选择Issues严重级别")
    print("=" * 60)
    print("可选项：BLOCKER, CRITICAL, MAJOR, MINOR, INFO")
    print("提示：输入多个级别用逗号分隔（如：BLOCKER,CRITICAL,MAJOR）")
    print("      直接回车表示导出所有级别")
    print("=" * 60)

    choice = input("请选择严重级别: ").strip()

    if not choice:
        return None  # 返回None表示不过滤，获取所有级别

    # 验证输入
    valid_levels = ["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
    selected = [level.strip().upper() for level in choice.split(",")]

    # 过滤无效级别
    valid_selected = [level for level in selected if level in valid_levels]
    invalid_selected = [level for level in selected if level not in valid_levels]

    if invalid_selected:
        print(f"警告：以下无效级别将被忽略: {', '.join(invalid_selected)}")
        print(f"有效级别: {', '.join(valid_levels)}")

    if not valid_selected:
        print("未选择有效级别，将导出所有严重级别")
        return None

    return ",".join(valid_selected)


def select_status():
    """选择要导出的Issues状态（OPEN为必选项）"""
    print("\n" + "=" * 60)
    print("选择Issues状态")
    print("=" * 60)
    print("可选项：OPEN, CONFIRMED, REOPENED, RESOLVED, CLOSED, REVIEWED")
    print("提示：OPEN状态是必须包含的")
    print("      可选择其他状态，用逗号分隔（如：CONFIRMED,REOPENED）")
    print("      直接回车表示仅导出OPEN状态")
    print("=" * 60)

    choice = input("请选择额外状态 [无]: ").strip()

    # OPEN状态是必须的
    selected_statuses = ["OPEN"]

    if not choice:
        return ",".join(selected_statuses)  # 仅OPEN

    # 验证输入
    valid_statuses = ["CONFIRMED", "REOPENED", "RESOLVED", "CLOSED", "REVIEWED"]
    selected = [status.strip().upper() for status in choice.split(",")]

    # 过滤无效状态
    valid_selected = [status for status in selected if status in valid_statuses]
    invalid_selected = [status for status in selected if status not in valid_statuses]

    if invalid_selected:
        print(f"警告：以下无效状态将被忽略: {', '.join(invalid_selected)}")
        print(f"有效状态: {', '.join(valid_statuses)}")

    # 将有效状态添加到OPEN之后
    selected_statuses.extend(valid_selected)

    return ",".join(selected_statuses)


def fetch_all_issues(
    config, branch=None, pr_number=None, severities=None, statuses="OPEN"
):
    """获取issues，支持分支、PR、严重级别和状态过滤"""
    auth = base64.b64encode(f"{config['sonar_token']}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}

    all_issues = []
    page = 1
    page_size = 500

    if pr_number:
        print(f"正在获取PR #{pr_number} 的issues")
    elif branch:
        print(f"正在获取分支 '{branch}' 的issues")
    else:
        print("正在获取所有分支汇总的issues")
    print(f"项目: {config['project_key']}")
    print(f"组织: {config['organization']}")
    if severities:
        print(f"严重级别: {severities}")
    print(f"状态: {statuses}")
    print("=" * 50)

    params = {
        "componentKeys": config["project_key"],
        "organization": config["organization"],
        "ps": page_size,
        "p": page,
        "statuses": statuses,  # 使用传入的状态参数，默认为OPEN
    }

    if severities:
        params["severities"] = severities  # 添加严重级别过滤

    if pr_number:
        params["pullRequest"] = pr_number
    elif branch:
        params["branch"] = branch

    total_fetched = 0
    total_from_api = None

    while True:
        try:
            response = requests.get(
                API_URL,
                headers=headers,
                params=params,
                timeout=30,
            )
            if response.status_code != 200:
                print(f"HTTP错误: {response.status_code}")
                print(f"响应: {response.text[:200]}")
                return None

            data = response.json()

            if total_from_api is None:
                total_from_api = data.get("total", 0)
                print(f"API报告总issues数: {total_from_api}")
                if total_from_api == 0:
                    print("警告：API返回0 issues，请检查配置")

            issues = data.get("issues", [])

            if not issues:
                print(f"第{page}页无数据，结束")
                break

            for issue in issues:
                all_issues.append(
                    {
                        "Issue Key": issue.get("key"),
                        "类型": issue.get("type"),
                        "严重级别": issue.get("severity"),
                        "状态": issue.get("status"),
                        "文件路径": issue.get("component", "").split(":")[-1],
                        "行号": issue.get("line", ""),
                        "问题描述": issue.get("message"),
                        "创建时间": issue.get("creationDate"),
                        "作者": issue.get("author", "N/A"),
                        "规则": issue.get("rule", "").split(":")[-1],
                        "分支": branch or "汇总",
                        "PR编号": pr_number or "N/A",
                    }
                )

            total_fetched += len(issues)
            print(f"已加载第{page}页: {len(issues)}条 (累计: {total_fetched})")

            if len(issues) < page_size:
                break

            page += 1
            params["p"] = page

        except requests.exceptions.JSONDecodeError:
            print("响应解析失败，可能不是有效JSON")
            print(f"原始响应: {response.text[:300]}")
            return None
        except requests.exceptions.Timeout:
            print("请求超时，请检查网络")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None

    return all_issues


def export_to_excel(issues, filename):
    """导出为Excel格式"""
    try:
        df = pd.DataFrame(issues)

        column_order = [
            "Issue Key",
            "类型",
            "严重级别",
            "状态",
            "文件路径",
            "行号",
            "问题描述",
            "创建时间",
            "作者",
            "规则",
            "分支",
            "PR编号",
        ]
        df = df[column_order]

        df.to_excel(filename, index=False, engine="openpyxl")
        return True
    except Exception as e:
        print(f"Excel导出失败: {e}")
        return False


def export_to_csv(issues, filename):
    """导出为CSV格式"""
    try:
        df = pd.DataFrame(issues)

        df.columns = [
            "Issue Key",
            "Type",
            "Severity",
            "Status",
            "File Path",
            "Line",
            "Message",
            "Created",
            "Author",
            "Rule",
            "Branch",
            "PR",
        ]

        df.to_csv(filename, index=False, encoding="utf-8-sig")
        return True
    except Exception as e:
        print(f"CSV导出失败: {e}")
        return False


def export_to_json(issues, filename, config):
    """导出为JSON格式"""
    try:
        output_data = {
            "metadata": {
                "project": config["project_key"],
                "organization": config["organization"],
                "branch": config.get("branch", "main"),
                "pr_number": config.get("pr_number", ""),
                "exported_at": datetime.now().isoformat(),
                "total_issues": len(issues),
                "version": CURRENT_VERSION,
            },
            "issues": issues,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"JSON导出失败: {e}")
        return False


def show_export_menu(config):
    """显示导出格式选择菜单"""
    print("\n" + "=" * 60)
    print("选择导出格式")
    print("=" * 60)
    print("(1) Excel (.xlsx) - 适合表格查看与分析")
    print("(2) CSV (.csv) - 适合导入数据库或其他系统")
    print("(3) JSON (.json) - 适合程序处理与备份")
    print("-" * 60)
    print("提示：可以输入多个数字，用逗号分隔（如1,3）")
    print("      输入0返回主菜单")
    print("=" * 60)

    while True:
        choice = input("\n请输入选项: ").strip()

        if choice == "0":
            return None

        # 验证输入
        selected = []
        for item in choice.split(","):
            item = item.strip()
            if item in ["1", "2", "3"]:
                selected.append(item)
            else:
                print(f"无效选项: {item}")
                break

        if selected:
            return selected

        print("请重新选择")


def get_latest_version():
    """从GitHub API获取最新版本号"""
    try:
        print("提示：正在查询最新版本...")
        response = requests.get(GITHUB_API_URL, timeout=10)
        if response.status_code != 200:
            print(f"警告：无法获取最新版本信息 (HTTP {response.status_code})")
            return None

        data = response.json()
        tag_name = data.get("tag_name", "")

        if not tag_name:
            print("警告：响应中没有tag_name字段")
            return None

        print(f"提示：远程版本: {tag_name}")
        return tag_name

    except Exception as e:
        print(f"警告：获取版本信息失败: {e}")
        return None


def check_for_updates():
    """检查并下载更新"""
    print("\n" + "=" * 60)
    print("检查更新")
    print("=" * 60)

    # 获取最新版本
    latest_tag = get_latest_version()
    if not latest_tag:
        print("提示：无法获取最新版本信息")
        return False

    print(f"当前版本: {CURRENT_VERSION}")
    print(f"远程版本: {latest_tag}")

    # 比较版本
    if latest_tag == CURRENT_VERSION:
        print("提示：当前已是最新版本")
        return False

    print("-" * 60)
    print("发现新版本!")
    print("-" * 60)

    # 确认是否更新
    confirm = input("确认更新?(y/N): ").strip().lower()
    if confirm != "y":
        print("提示：取消更新")
        return False

    # 构建下载URL
    download_url = f"{UPDATE_BASE_URL.format(version=latest_tag)}/sonarcloud_issues-{latest_tag}-win.exe"
    print(f"提示：下载地址: {download_url}")
    print(f"提示：文件大小可能较大，请耐心等待...")

    # 临时文件路径
    temp_file = os.path.join(
        tempfile.gettempdir(), f"sonarcloud_issues_{latest_tag}.exe"
    )

    print("\n提示：开始下载...")

    # 执行下载
    if not download_file(download_url, temp_file):
        print("错误：下载失败")
        return False

    # 验证文件
    if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
        print("错误：下载文件无效或为空")
        try:
            os.remove(temp_file)
        except:
            pass
        return False

    # 获取当前exe路径
    current_exe = sys.executable
    backup_exe = current_exe + ".old"

    print("提示：正在替换文件...")

    # 删除旧备份
    if os.path.exists(backup_exe):
        try:
            os.remove(backup_exe)
            print("提示：已删除旧备份文件")
        except Exception as e:
            print(f"警告：无法删除旧备份: {e}")

    # 重命名当前exe为备份
    try:
        os.rename(current_exe, backup_exe)
        print("提示：已创建备份文件: " + backup_exe)
    except Exception as e:
        print(f"错误：无法重命名当前文件: {e}")
        print("提示：请确保程序有写入权限")
        try:
            os.remove(temp_file)
        except:
            pass
        return False

    # 移动新文件到当前位置
    try:
        shutil.move(temp_file, current_exe)
        print("提示：新文件已替换完成")
    except Exception as e:
        print(f"错误：无法移动新文件: {e}")
        print("提示：尝试恢复备份...")
        # 恢复旧文件
        if os.path.exists(backup_exe):
            shutil.move(backup_exe, current_exe)
            print("提示：已恢复为旧版本")
        return False

    print("-" * 60)
    print("成功：更新完成!")
    print(f"程序路径: {current_exe}")
    print(f"备份路径: {backup_exe}")
    print("\n提示：请重新启动程序以使用新版本")
    print("=" * 60)

    return True


def download_file(url, dest_path):
    """下载文件并显示进度"""
    try:
        response = requests.get(url, stream=True, timeout=120)  # 增加超时时间
        if response.status_code != 200:
            print(f"错误：HTTP {response.status_code}")
            if response.status_code == 404:
                print("提示：文件不存在，可能版本号错误或文件未上传")
            print(f"响应: {response.text[:200] if response.text else '无响应内容'}")
            return False

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 显示进度
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(
                            f"\r提示：下载进度 {percent:.1f}% ({downloaded}/{total_size} bytes)",
                            end="",
                        )

        print()  # 换行
        return True

    except requests.exceptions.Timeout:
        print("\n错误：请求超时，请检查网络或稍后重试")
        return False
    except Exception as e:
        print(f"\n错误：下载失败: {e}")
        return False


def show_main_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("SonarCloud Issues 主菜单")
    print("=" * 60)
    print("(1) 导出Issues")
    print("(2) 设置")
    print("(0) 退出程序")
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print(f"SonarCloud Issues v{CURRENT_VERSION}")
    print("支持多格式导出")
    print("=" * 60)

    # 确保配置存在
    config = get_config_or_prompt()

    while True:
        show_main_menu()
        choice = input("请选择: ").strip()

        if choice == "0":
            print("退出程序")
            break
        elif choice == "1":
            # 步骤1：选择是否按严重级别过滤
            use_severity = input("\n是否按严重级别过滤issues? (y/N): ").strip().lower()
            severities = None
            if use_severity == "y":
                severities = select_severity_levels()
                if severities is None:
                    print("提示：取消严重级别过滤")
                else:
                    print(f"提示：已选择严重级别: {severities}")

            # 步骤2：选择是否按状态过滤（OPEN为必选项）
            use_status = (
                input("\n是否选择其他状态（OPEN已默认包含）? (y/N): ").strip().lower()
            )
            statuses = "OPEN"  # 默认只导出OPEN
            if use_status == "y":
                statuses = select_status()
                print(f"提示：已选择状态: {statuses}")
            else:
                print("提示：仅导出OPEN状态的issues")

            # 步骤3：选择导出范围
            branch, pr_number = select_scope(config)
            if branch is None and pr_number is None and choice != "4":
                continue

            # 步骤4：获取数据
            issues = fetch_all_issues(config, branch, pr_number, severities, statuses)

            if issues is None:
                print("\n导出失败，请检查错误信息")
                continue

            if not issues:
                print("\n未找到任何issues")
                print("\n排查步骤:")
                print("1. 确认TOKEN是User Token（不是Project Token）")
                print("2. 访问 https://sonarcloud.io/account/security/   重新生成")
                print("3. 确认Organization Key为: cola-pig1121（小写）")
                print("4. 确认Project Key是否正确")
                print("5. 确认分支/PR是否存在")
                print("6. 在浏览器测试此链接:")
                print(
                    f"   https://sonarcloud.io/api/issues/search?componentKeys={config['project_key']}&organization={config['organization']}&ps=10"
                )
                continue

            # 步骤5：选择导出格式
            export_choices = show_export_menu(config)
            if export_choices is None:
                continue

            # 步骤6：执行导出
            print("\n" + "=" * 60)
            print("开始导出...")
            print("=" * 60)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            success = False

            for choice in export_choices:
                if choice == "1":
                    filename = f"{OUTPUT_PREFIX}_{timestamp}.xlsx"
                    print(f"\n[Excel] 导出: {filename}")
                    if export_to_excel(issues, filename):
                        print("    完成")
                        success = True

                elif choice == "2":
                    filename = f"{OUTPUT_PREFIX}_{timestamp}.csv"
                    print(f"\n[CSV] 导出: {filename}")
                    if export_to_csv(issues, filename):
                        print("    完成")
                        success = True

                elif choice == "3":
                    filename = f"{OUTPUT_PREFIX}_{timestamp}.json"
                    print(f"\n[JSON] 导出: {filename}")
                    if export_to_json(issues, filename, config):
                        print("    完成")
                        success = True

            # 最终报告
            print("\n" + "=" * 60)
            if success:
                print("导出完成!")
                print(f"文件保存在: {os.getcwd()}")
            else:
                print("导出失败，请检查错误信息")
            print("=" * 60)

        elif choice == "2":
            show_settings_menu()
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()
