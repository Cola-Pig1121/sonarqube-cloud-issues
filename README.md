# SonarCloud Issues

一个用于从SonarCloud导出issues并支持多种格式（Excel、CSV、JSON）导出的Python工具。

## 功能特性

- **多格式导出**: 支持Excel(.xlsx)、CSV(.csv)、JSON(.json)三种格式导出
- **完整数据**: 导出包含Issue Key、类型、严重级别、状态、文件路径、行号、问题描述、创建时间、作者、规则等完整信息
- **分页获取**: 自动处理大量issues的分页获取
- **交互式配置**: 友好的配置界面，支持单独配置各个参数
- **配置安全**: 本地安全存储配置，Token显示脱敏
- **详细日志**: 实时显示获取进度和状态信息
- **容错处理**: 完善的错误处理和用户友好的错误提示

## 系统要求

- Python >= 3.11
- uv (包管理器)

## 安装说明

### 1. 获取项目
```bash
git clone https://github.com/Cola-Pig1121/sonarqube-cloud-issues.git
cd sonarqube-cloud-issues
```

### 2. 安装依赖
使用uv来安装项目依赖：
```bash
uv sync
```

### 3. 运行程序
```bash
uv run main.py
```

### 4. 打包程序
```bash
# 安装 UPX 压缩工具（可选，显著减小体积）
# 下载地址：https://github.com/upx/upx/releases
pyinstaller --onefile --name=sonarcloud_exporter --clean --upx-dir=/path/to/upx main.py
# 不使用upx：pyinstaller --onefile --name=sonarcloud_exporter --clean main.py
```

## 配置说明

### 首次配置

首次运行程序时，需要配置以下参数：

1. **SonarCloud User Token**
   - 访问 [SonarCloud My Account](https://sonarcloud.io/account/security/)
   - 进入 "Security" 页面
   - 点击 "Generate Token"
   - 选择 "User Token" 类型
   - 复制生成的Token

2. **Project Key**
   - 在SonarCloud中找到你的项目
   - 项目Key格式通常为：`organization_projectname`
   - 示例：`colapig1121_myproject`

3. **Organization Key**
   - 你的组织名称（小写）
   - 示例：`colapig1121`

### 配置菜单功能

程序提供完整的设置管理功能：

- **配置SonarCloud Token**: 更新用户令牌
- **配置Project Key**: 更新项目标识符
- **配置Organization Key**: 更新组织标识符
- **查看当前配置**: 显示当前配置（Token会脱敏显示）
- **重新配置所有设置**: 重新设置所有参数

## 使用方法

### 启动程序
```bash
uv run main.py
```

### 主菜单功能

1. **导出Issues**: 开始导出流程
2. **设置**: 进入配置管理菜单
0. **退出程序**: 退出应用

### 导出流程

1. 选择 "导出Issues"
2. 程序会自动获取所有issues（支持分页）
3. 选择导出格式：
   - **Excel (.xlsx)**: 适合表格查看与分析
   - **CSV (.csv)**: 适合导入数据库或其他系统
   - **JSON (.json)**: 适合程序处理与备份
4. 可以同时选择多种格式（用逗号分隔，如：1,3）
5. 导出完成后，文件会保存在当前目录下

### 导出文件名格式

- Excel: `sonarqube_issues_YYYYMMDD_HHMMSS.xlsx`
- CSV: `sonarqube_issues_YYYYMMDD_HHMMSS.csv`
- JSON: `sonarqube_issues_YYYYMMDD_HHMMSS.json`

## 导出的数据字段

| 字段名 | 说明 |
|--------|------|
| Issue Key | SonarCloud生成的唯一标识符 |
| 类型 | Bug、Vulnerability、Code Smell等 |
| 严重级别 | BLOCKER、CRITICAL、MAJOR、MINOR、INFO |
| 状态 | OPEN、CLOSED、RESOLVED、REOPENED |
| 文件路径 | 存在问题的源文件路径 |
| 行号 | 问题所在的行号 |
| 问题描述 | 问题的详细描述 |
| 创建时间 | 问题创建的时间戳 |
| 作者 | 问题创建者 |
| 规则 | 触发问题的Sonar规则 |

## 故障排除

### 常见问题

1. **API返回0 issues**
   - 检查Token是否为User Token（不是Project Token）
   - 确认Organization Key和Project Key是否正确
   - 访问浏览器测试API链接验证配置

2. **HTTP错误**
   - 检查网络连接
   - 验证Token是否有效
   - 确认Project Key是否存在于指定的Organization中

3. **配置文件丢失**
   - 删除`.sonarcloud_config.json`文件重新配置
   - 或使用"重新配置所有设置"功能

### 调试方法

程序会在控制台显示详细的处理信息：
- 项目和组织信息
- API返回的总issues数量
- 每页获取的进度
- 错误信息和响应内容

## 文件结构

```
sonarqube-cloud-issues/
├── main.py                 # 主程序入口文件
├── pyproject.toml         # uv项目管理配置
├── README.md              # 项目说明文档
├── .sonarcloud_config.json # 用户配置文件（自动生成）
└── *.xlsx,*.csv,*.json    # 导出的issues报告文件
```

## 技术实现

### 依赖包
- **requests**: HTTP请求处理
- **pandas**: 数据处理和CSV导出
- **openpyxl**: Excel文件生成
- **json**: 配置和数据处理

### 核心功能
- **分页获取**: 自动处理大量数据的分页请求
- **认证机制**: 使用Base64编码的用户名:密码认证
- **数据转换**: 将API数据转换为标准化格式
- **多格式导出**: 支持Excel、CSV、JSON三种输出格式
- **配置管理**: 安全的本地配置存储

## 版本信息

- **当前版本**: v3.0
- **Python要求**: >=3.11
- **开发语言**: Python 3

## 许可证

MIT License

Copyright (c) 2025 SonarCloud Issues

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 技术支持

如果在使用过程中遇到问题，可以按照以下步骤进行排查：

1. 先查看本文档中的故障排除部分，通常能找到常见问题的解决方案
2. 确认配置的参数是否正确，特别是Organization Key和Project Key
3. 查看程序运行时的控制台输出，里面会有详细的错误信息帮助定位问题

---
