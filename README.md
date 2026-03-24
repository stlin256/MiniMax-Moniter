# MiniMax Monitor Tool

一个现代化的、半透明置顶的 MiniMax API 用量监控工具。

## 功能特点
- **实时监控**：每秒更新一次 API 用量信息。
- **RPM 计算**：实时显示每分钟请求数 (Requests Per Minute)。
- **现代化 UI**：使用 PyQt6 构建，支持真正的 Windows 无边框、半透明、毛玻璃质感显示。
- **可拖拽**：点击窗口任意区域即可轻松拖动。
- **自动处理周期**：自动识别 MiniMax-M* 的 5 小时滚动周期及其他模型的 24 小时刷新周期。
- **安全存储**：API Key 以 Base64 格式加密存储。

## 如何运行
1. 确保安装了 Python 3.11+。
2. 安装依赖：
   ```bash
   pip install PyQt6 requests
   ```
3. 启动程序：
   ```bash
   python app.py
   ```

## 如何打包成 EXE
1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 执行打包命令：
   ```bash
   pyinstaller --noconsole --onefile --name "MiniMaxMonitor" app.py
   ```

## 注意事项
- 第一次启动时，点击右上角的设置按钮配置您的 API Key。
- `config.b64` 文件包含您的凭据，请勿上传至公开仓库。
