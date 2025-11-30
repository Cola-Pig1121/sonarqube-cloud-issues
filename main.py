#!/usr/bin/env python3
"""
SonarCloud Issues
Usage: uv run main.py
"""

import base64
import json
import os
import sys
from datetime import datetime

import pandas as pd
import requests

# ==================== 配置文件路径 ====================
CONFIG_FILE = ".sonarcloud_config.json"
# API端点
API_URL = "https://sonarcloud.io/api/issues/search"
# 输出文件名前缀
OUTPUT_PREFIX = "sonarcloud_issues"
# ====================================================


def load_config():
    """从配置文件加载配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
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

        config = {
            "sonar_token": token,
            "project_key": project_key,
            "organization": organization,
            "created_at": datetime.now().isoformat(),
        }

        return config
    except KeyboardInterrupt:
        print("\n取消配置")
        return None


def show_settings_menu():
    """显示设置菜单"""
    while True:
        print("\n" + "=" * 60)
        print("设置菜单")
        print("=" * 60)
        print("(1) 配置SonarCloud Token")
        print("(2) 配置Project Key")
        print("(3) 配置Organization Key")
        print("(4) 查看当前配置")
        print("(5) 重新配置所有设置")
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
            view_config()
        elif choice == "5":
            reconfigure_all()
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
    """查看当前配置（隐藏Token部分）"""
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
    print(f"创建时间: {config.get('created_at', '未知')}")
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


def fetch_all_issues(config):
    """从SonarCloud获取所有issues"""
    auth = base64.b64encode(f"{config['sonar_token']}:".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}

    all_issues = []
    page = 1
    page_size = 500

    print(f"正在获取项目: {config['project_key']}")
    print(f"组织: {config['organization']}")
    print("=" * 50)

    params = {
        "componentKeys": config["project_key"],
        "organization": config["organization"],
        "ps": page_size,
        "p": page,
        "statuses": "OPEN,CLOSED,RESOLVED,REOPENED",
    }

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

            # 首次请求获取总数
            if total_from_api is None:
                total_from_api = data.get("total", 0)
                print(f"API报告总issues数: {total_from_api}")
                if total_from_api == 0:
                    print("警告：API返回0 issues，请检查配置")

            issues = data.get("issues", [])

            if not issues:
                print(f"第{page}页无数据，结束")
                break

            # 提取关键字段
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
                    }
                )

            print(f"已加载第{page}页: {len(issues)}条 (累计: {len(all_issues)})")

            # 检查是否还有更多页
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

        # CSV使用英文列名避免编码问题
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
                "exported_at": datetime.now().isoformat(),
                "total_issues": len(issues),
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


def show_main_menu():
    """显示主菜单"""
    print("\n" + "=" * 60)
    print("SonarCloud Issues Exporter 主菜单")
    print("=" * 60)
    print("(1) 导出Issues")
    print("(2) 设置")
    print("(0) 退出程序")
    print("=" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("SonarCloud Issues Exporter v3.0")
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
            # 导出流程
            issues = fetch_all_issues(config)

            if issues is None:
                print("\n导出失败，请检查错误信息")
                continue

            if not issues:
                print("\n未找到任何issues")
                print("\n排查步骤:")
                print("1. 确认TOKEN是User Token（不是Project Token）")
                print("2. 访问 https://sonarcloud.io/account/security/ 重新生成")
                print("3. 确认Organization Key为: cola-pig1121（小写）")
                print("4. 确认Project Key是否正确")
                print("5. 在浏览器测试此链接:")
                print(
                    f"   https://sonarcloud.io/api/issues/search?componentKeys={config['project_key']}&organization={config['organization']}&ps=10"
                )
                continue

            # 选择导出格式
            export_choices = show_export_menu(config)
            if export_choices is None:
                continue

            # 执行导出
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
