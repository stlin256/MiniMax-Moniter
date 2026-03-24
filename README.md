# MiniMax Monitor Tool

![Preview](img.png)

[English](#english) | [简体中文](#chinese)

<a name="english"></a>
## English

A modern, real-time quota monitor for MiniMax API developers. Features a semi-transparent floating UI, precise RPM tracking, and smooth non-linear animations.

### Features
- **Real-time Monitoring**: Fetches API usage every second.
- **RPM Tracking**: Precise Requests Per Minute (RPM) calculation based on a 60-second sliding window.
- **Modern UI**: Built with PyQt6, featuring frameless, semi-transparent, and glassmorphism effects.
- **Immersive Interaction**: Buttons, borders, and resize handles are hidden by default and reveal smoothly on hover.
- **Non-linear Animations**: Smooth transition animations for the UI elements using `InOutQuad` easing curves.
- **Intelligent Cycles**: Automatically handles MiniMax-M* 5-hour rolling windows and other models' 24-hour refresh cycles.
- **Usage History**: Automatically saves all request results to `usage_history.csv` for audit and tracking, indexed by the last 6 digits of your API Key.
- **Smart Persistence**: Remembers your API Key, display mode (Used/Remains), opacity, window position, and size.
- **System Tray**: Runs in the background with a system tray icon for continuous monitoring.

### Quick Start
1. Ensure you have Python 3.11+ installed.
2. Install dependencies:
   ```bash
   pip install PyQt6 requests
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. **Configuration**: Click the ⚙ icon (visible on hover) to set your API Key.

### Build to EXE
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Run the build command:
   ```bash
   pyinstaller --noconsole --onefile --name "MiniMaxMonitor" app.py
   ```

---

<a name="chinese"></a>
## 简体中文

一款专为 MiniMax API 开发者打造的现代化实时用量监控工具。支持半透明悬浮窗、RPM 精准追踪、平滑非线性动画及高度自定义配置。

### 功能特点
- **实时监控**：每秒更新一次 API 用量信息。
- **RPM 追踪**：基于 60 秒滑动窗口精准计算每分钟请求数 (Requests Per Minute)。
- **现代化 UI**：使用 PyQt6 构建，支持真正的无边框、半透明毛玻璃质感显示。
- **沉浸式交互**：设置按钮、外框线及缩放手柄平时完全隐藏，鼠标移入时优雅浮现。
- **非线性动画**：UI 元素移动采用 `InOutQuad` 缓动曲线，交互极其丝滑。
- **自动处理周期**：自动识别 MiniMax-M* 的 5 小时滚动窗口及其它模型的 24 小时刷新周期。
- **用量历史存证**：自动将所有请求结果保存至 `usage_history.csv`，并以 API Key 后 6 位作为索引，方便追溯审计。
- **配置持久化**：自动记忆 API Key、显示模式（已用/余量）、透明度、窗口坐标及尺寸。
- **系统托盘**：支持最小化至托盘后台运行，点击关闭不中断监控。

### 快速启动
1. 确保安装了 Python 3.11+。
2. 安装依赖：
   ```bash
   pip install PyQt6 requests
   ```
3. 启动程序：
   ```bash
   python app.py
   ```
4. **配置**：点击窗口右上角的齿轮图标（鼠标移入可见）进入配置页面。

### 如何打包成 EXE
1. 安装 PyInstaller：
   ```bash
   pip install pyinstaller
   ```
2. 执行打包命令：
   ```bash
   pyinstaller --noconsole --onefile --name "MiniMaxMonitor" app.py
   ```

## License
MIT License
