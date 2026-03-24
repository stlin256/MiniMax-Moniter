import sys
import threading
import time
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QLineEdit, QComboBox, QFrame,
                             QSystemTrayIcon, QMenu, QSizeGrip, QStackedWidget, QSlider)
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal, QObject, QThread, QRect, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QAction

from config_manager import load_config, save_config
from monitor import UsageMonitor

# Custom Colors
ROSE_RED = "#D81B60"
ROSE_RED_LIGHT = "#F06292"

class MonitorWorker(QObject):
    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, api_key, model_name):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name
        self.monitor = UsageMonitor(api_key, model_name)
        self._running = True

    def run(self):
        while self._running:
            if self.api_key:
                try:
                    success = self.monitor.update()
                    if success:
                        data = {
                            "usage": self.monitor.get_usage_str(),
                            "rpm": self.monitor.get_rpm(),
                            "interval": self.monitor.get_interval_str().replace("Cycle: ", ""),
                            "model": self.monitor.model_name
                        }
                        self.data_updated.emit(data)
                    else:
                        self.error_occurred.emit(self.monitor.error_message or "Unknown error")
                except Exception as e:
                    self.error_occurred.emit(str(e))
            for _ in range(10):
                if not self._running: break
                time.sleep(0.1)

    def stop(self):
        self._running = False

class MiniMaxMonitor(QWidget):
    def __init__(self):
        super().__init__()
        cfg = load_config()
        self.api_key = cfg.get("api_key", "")
        self.model_name = cfg.get("model", "MiniMax-M*")
        self.bg_opacity = cfg.get("opacity", 230)
        self.last_geometry = cfg.get("geometry")
        
        self.worker = None
        self.thread = None
        self._is_config = False
        
        self.initUI()
        self.initTray()
        self.startWorker()
        
        if self.last_geometry:
            self.setGeometry(self.last_geometry["x"], self.last_geometry["y"], 
                             self.last_geometry["w"], self.last_geometry["h"])
        
        if not self.api_key:
            QTimer.singleShot(500, self.show_config_and_warn)

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        
        self.main_layout = QVBoxLayout(); self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.container = QFrame(); self.container.setObjectName("MainContainer")
        self.updateStyle(); self.main_layout.addWidget(self.container)

        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(10, 6, 10, 6); self.container_layout.setSpacing(0)

        # Header
        self.header_widget = QWidget()
        self.header_widget.setFixedHeight(24)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 0, 0, 0); self.header_layout.setSpacing(0)
        
        self.title_lbl = QLabel("MiniMax")
        self.title_lbl.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {ROSE_RED_LIGHT};")
        self.header_layout.addWidget(self.title_lbl)
        
        self.right_container = QWidget()
        self.header_layout.addWidget(self.right_container, 1)
        
        self.interval_label = QLabel("--:-- - --:--", self.right_container)
        self.interval_label.setStyleSheet("font-size: 9px; color: #777; font-weight: bold;")
        self.interval_label.setFixedHeight(24)
        
        self.btn_settings = QPushButton("⚙", self.right_container)
        self.btn_settings.setFixedSize(18, 18); self.btn_settings.setObjectName("HeaderBtn")
        self.btn_settings.clicked.connect(self.toggle_config)
        self.btn_settings.move(0, 3); self.btn_settings.setVisible(False)
        
        self.btn_close = QPushButton("×", self.right_container)
        self.btn_close.setFixedSize(18, 18); self.btn_close.setObjectName("HeaderBtn")
        self.btn_close.clicked.connect(self.hide)
        self.btn_close.move(20, 3); self.btn_close.setVisible(False)
        
        self.anim = QPropertyAnimation(self.interval_label, b"pos")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.container_layout.addWidget(self.header_widget)

        # View Stack
        self.view_stack = QStackedWidget()
        self.monitor_view = QWidget(); m_layout = QVBoxLayout(self.monitor_view)
        m_layout.setContentsMargins(0, 0, 0, 0); m_layout.setSpacing(0)
        self.usage_label = QLabel("0 / 0"); self.usage_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        m_sep = QFrame(); m_sep.setFrameShape(QFrame.Shape.HLine); m_sep.setStyleSheet(f"background-color: {ROSE_RED}; height: 1px; border: none; margin: 3px 0;")
        m_footer = QHBoxLayout(); self.rpm_label = QLabel("RPM: 0"); self.rpm_label.setStyleSheet("font-size: 10px; color: #DDD;")
        self.model_label = QLabel(self.model_name); self.model_label.setStyleSheet(f"font-size: 10px; color: {ROSE_RED_LIGHT}; font-weight: bold;")
        m_footer.addWidget(self.rpm_label); m_footer.addStretch(); m_footer.addWidget(self.model_label)
        m_layout.addWidget(self.usage_label); m_layout.addWidget(m_sep); m_layout.addLayout(m_footer)
        
        self.config_view = QWidget(); c_layout = QVBoxLayout(self.config_view)
        c_layout.setContentsMargins(0, 4, 0, 4); c_layout.setSpacing(5)
        self.input_key = QLineEdit(self.api_key); self.input_key.setPlaceholderText("API Key..."); self.input_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_key.setStyleSheet("background: rgba(255,255,255,20); color: white; border: 1px solid #444; border-radius: 4px; padding: 2px 5px; min-height: 20px;")
        self.combo_model = QComboBox(); self.combo_model.addItems(["MiniMax-M*", "speech-hd", "image-01", "music-2.5"])
        self.combo_model.setCurrentText(self.model_name); self.combo_model.setStyleSheet("background: rgba(255,255,255,20); color: white; border: 1px solid #444; min-height: 20px; border-radius: 4px;")
        opacity_row = QHBoxLayout(); opacity_row.addWidget(QLabel("Opacity", styleSheet="font-size: 9px; color: #AAA;"))
        self.slider_opacity = QSlider(Qt.Orientation.Horizontal); self.slider_opacity.setRange(40, 255); self.slider_opacity.setValue(self.bg_opacity); self.slider_opacity.setFixedHeight(16); self.slider_opacity.valueChanged.connect(self.onOpacityChanged); opacity_row.addWidget(self.slider_opacity)
        self.config_msg = QLabel(""); self.config_msg.setStyleSheet("font-size: 9px; color: #F44; font-weight: bold;")
        btn_save = QPushButton("Save && Apply"); btn_save.setStyleSheet(f"background: {ROSE_RED}; color: white; border-radius: 4px; min-height: 24px; font-weight: bold;")
        btn_save.clicked.connect(self.save_config_action)
        btn_back = QPushButton("Back"); btn_back.setStyleSheet("font-size: 9px; color: #AAA;"); btn_back.clicked.connect(self.toggle_config)
        c_layout.addWidget(self.input_key); c_layout.addWidget(self.combo_model); c_layout.addLayout(opacity_row); c_layout.addWidget(self.config_msg); c_layout.addWidget(btn_save); c_layout.addWidget(btn_back)

        self.view_stack.addWidget(self.monitor_view); self.view_stack.addWidget(self.config_view)
        self.container_layout.addWidget(self.view_stack)

        self.sizegrip = QSizeGrip(self); self.sizegrip.setFixedSize(12, 12); self.sizegrip.setVisible(False)
        self.oldPos = self.pos()
        if not self.last_geometry: 
            self.setMinimumSize(150, 75)
            self.resize(180, 90)
        else:
            self.setMinimumSize(150, 75)

    def onOpacityChanged(self, value):
        self.bg_opacity = value; self.updateStyle()

    def updateStyle(self, hovered=False):
        border_color = ROSE_RED if hovered else "rgba(0,0,0,0)"
        self.container.setStyleSheet(f"""
            #MainContainer {{
                background-color: rgba(20, 20, 20, {self.bg_opacity});
                border: 2px solid {border_color};
                border-radius: 12px;
            }}
            #HeaderBtn {{ 
                background-color: transparent; color: white; border: none; font-size: 16px; font-weight: bold;
            }}
            QPushButton#HeaderBtn:hover {{ color: {ROSE_RED_LIGHT}; }}
            QSlider::handle:horizontal {{ background: {ROSE_RED}; width: 12px; border-radius: 6px; }}
        """)

    def update_header_positions(self, hovered):
        w = self.right_container.width()
        self.btn_settings.move(w - 40, 3)
        self.btn_close.move(w - 18, 3)
        
        self.btn_settings.setVisible(hovered)
        self.btn_close.setVisible(hovered)
        
        target_x = 0
        if hovered:
            # Move interval to the left of buttons
            target_x = w - 45 - self.interval_label.width()
        else:
            # Move interval to the far right
            target_x = w - self.interval_label.width()
            
        self.anim.stop()
        self.anim.setEndValue(QPoint(int(target_x), 0))
        self.anim.start()

    def enterEvent(self, event):
        self.updateStyle(hovered=True); self.sizegrip.setVisible(True)
        self.update_header_positions(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.updateStyle(hovered=False); self.sizegrip.setVisible(False)
        self.update_header_positions(False)
        super().leaveEvent(event)

    def shrink_window(self):
        self.setMinimumSize(150, 75)
        self.resize(170, 85)

    def expand_window(self):
        self.setMinimumSize(240, 160)
        self.resize(260, 180)

    def toggle_config(self):
        self._is_config = not self._is_config
        if self._is_config: self.expand_window(); self.view_stack.setCurrentIndex(1); self.btn_settings.setText("←")
        else: self.view_stack.setCurrentIndex(0); self.shrink_window(); self.btn_settings.setText("⚙")

    def persist_current_geometry(self):
        geom = self.geometry()
        self.last_geometry = {"x": geom.x(), "y": geom.y(), "w": geom.width(), "h": geom.height()}
        save_config(self.api_key, self.bg_opacity, self.model_name, self.last_geometry)

    def save_config_action(self):
        key = self.input_key.text().strip()
        if not key: self.config_msg.setText("Empty Key!"); return
        self.api_key = key; self.model_name = self.combo_model.currentText()
        self.persist_current_geometry()
        self.model_label.setText(self.model_name); self.startWorker(); self.config_msg.setText(""); self.toggle_config()

    def initTray(self):
        self.tray_icon = QSystemTrayIcon(self); self.tray_icon.setIcon(QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ComputerIcon))
        menu = QMenu(); menu.addAction(QAction("Show", self, triggered=self.show)); menu.addAction(QAction("Quit", self, triggered=QApplication.instance().quit))
        self.tray_icon.setContextMenu(menu); self.tray_icon.show(); self.tray_icon.activated.connect(self.onTrayActivated)

    def onTrayActivated(self, reason):
        try:
            if int(reason) in [3, 2]:
                if self.isVisible(): self.hide()
                else: self.showNormal(); self.activateWindow(); self.raise_()
        except: self.showNormal()

    def show_config_and_warn(self):
        if self.view_stack.currentIndex() == 0: self.toggle_config()
        self.config_msg.setText("Please configure API Key!")

    def startWorker(self):
        if self.worker: self.worker.stop()
        if self.thread: self.thread.quit(); self.thread.wait()
        self.thread = QThread(); self.worker = MonitorWorker(self.api_key, self.model_name); self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run); self.worker.data_updated.connect(self.updateDisplay); self.worker.error_occurred.connect(self.handleError)
        self.thread.start()

    def updateDisplay(self, data):
        self.usage_label.setText(data["usage"]); self.rpm_label.setText(f"RPM: {data['rpm']}")
        self.interval_label.setText(data["interval"]); self.interval_label.adjustSize()
        self.model_label.setText(data["model"])

    def handleError(self, msg):
        self.usage_label.setText("Error"); self.interval_label.setText(f"API Error")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            new_pos = self.pos() + delta
            screen = QApplication.primaryScreen().availableGeometry()
            new_pos.setX(max(screen.left(), min(new_pos.x(), screen.right() - self.width())))
            new_pos.setY(max(screen.top(), min(new_pos.y(), screen.bottom() - self.height())))
            self.move(new_pos); self.oldPos = event.globalPosition().toPoint(); self.persist_current_geometry()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sizegrip.move(self.width() - 14, self.height() - 14)
        self.persist_current_geometry()
        self.update_header_positions(self.underMouse())

if __name__ == '__main__':
    app = QApplication(sys.argv); app.setQuitOnLastWindowClosed(False); window = MiniMaxMonitor()
    window.show(); sys.exit(app.exec())
