import flet as ft
import threading
import time
from config_manager import load_api_key, save_api_key, has_api_key
from monitor import UsageMonitor
from minimax_api import MiniMaxAPI

def main(page: ft.Page):
    # App Settings
    page.title = "MiniMax Monitor"
    page.window_width = 300
    page.window_height = 200
    page.window_min_width = 300
    page.window_min_height = 200
    page.window_max_width = 300
    page.window_max_height = 200
    page.window_resizable = False
    page.window_always_on_top = True
    page.window_bgcolor = "transparent"
    page.bgcolor = "transparent"
    
    # Hide title bar and frame for modern look
    page.window_frameless = True
    page.window_title_bar_hidden = True
    page.window_title_bar_buttons_hidden = True
    
    # Data
    api_key = load_api_key()
    model_name = "MiniMax-M*"
    monitor = None
    if api_key:
        monitor = UsageMonitor(api_key, model_name)
    
    # UI Elements
    usage_text = ft.Text("0 / 0", size=24, weight="bold", color="white")
    rpm_text = ft.Text("RPM: 0", size=14, color="white70")
    interval_text = ft.Text("Cycle: -- : --", size=12, color="white54")
    model_label = ft.Text(model_name, size=12, color="cyan200")

    # Config Inputs
    api_key_input = ft.TextField(
        label="API Key", 
        value=api_key, 
        password=True, 
        can_reveal_password=True,
        border_color="cyan200",
        text_size=12
    )
    
    model_dropdown = ft.Dropdown(
        label="Model",
        options=[
            ft.dropdown.Option("MiniMax-M*"),
            ft.dropdown.Option("speech-hd"),
            ft.dropdown.Option("image-01"),
            ft.dropdown.Option("music-2.5"),
        ],
        value=model_name,
        border_color="cyan200",
        text_size=12,
    )

    def toggle_config(e):
        config_container.visible = not config_container.visible
        main_view_container.visible = not config_container.visible
        page.update()

    def save_config(e):
        nonlocal api_key, model_name, monitor
        api_key = api_key_input.value
        save_api_key(api_key)
        model_name = model_dropdown.value
        monitor = UsageMonitor(api_key, model_name)
        model_label.value = model_name
        toggle_config(None)

    # UI Containers
    # Use Padding and Border with new syntax
    main_view_container = ft.Container(
        content=ft.WindowDragArea(
            content=ft.Column([
                ft.Row([
                    ft.Text("MINIMAX MONITOR", size=10, weight="bold", color="cyan200", opacity=0.5),
                    ft.Row([
                        ft.IconButton("settings", icon_size=16, icon_color="white24", on_click=toggle_config),
                        ft.IconButton("close", icon_size=16, icon_color="white24", on_click=lambda _: page.window_close()),
                    ], spacing=0)
                ], alignment="spaceBetween"),
                
                ft.Column([
                    ft.Text("USED / TOTAL", size=10, color="white38"),
                    usage_text,
                    ft.Divider(height=1, color="white10"),
                    ft.Row([
                        ft.Column([
                            ft.Text("RPM", size=9, color="white38"),
                            rpm_text,
                        ], spacing=0),
                        ft.Column([
                            ft.Text("MODEL", size=9, color="white38"),
                            model_label,
                        ], spacing=0, horizontal_alignment="end"),
                    ], alignment="spaceBetween"),
                    interval_text,
                ], spacing=10, alignment="center", expand=True),
            ], spacing=0),
        ),
        padding=ft.Padding(15, 5, 15, 15), # (left, top, right, bottom)
        width=300,
        height=200,
        bgcolor="#aa121212", 
        border_radius=24,
        border=ft.Border(ft.BorderSide(1, "white10"), ft.BorderSide(1, "white10"), ft.BorderSide(1, "white10"), ft.BorderSide(1, "white10")),
        blur=ft.Blur(10, 10, "outer"), 
    )

    config_container = ft.Container(
        content=ft.Column([
            ft.Text("Configuration", size=16, weight="bold", color="white"),
            api_key_input,
            model_dropdown,
            ft.Button(content=ft.Text("Save & Apply"), on_click=save_config, bgcolor="cyan700", color="white"),
            ft.TextButton(content=ft.Text("Back", size=12), on_click=toggle_config),
        ], spacing=10),
        padding=20,
        width=300,
        height=200,
        bgcolor="#ee1a1a1a", 
        border_radius=20,
        visible=False
    )

    page.add(
        ft.Stack([
            main_view_container,
            config_container
        ])
    )

    def monitoring_loop():
        while True:
            try:
                if monitor:
                    success = monitor.update()
                    if success:
                        usage_text.value = monitor.get_usage_str()
                        rpm_text.value = f"RPM: {monitor.get_rpm()}"
                        interval_text.value = f"Cycle: {monitor.get_interval_str()}"
                    else:
                        usage_text.value = "Error"
                        rpm_text.value = (monitor.error_message or "Unknown error")[:30]
                    page.update()
            except Exception as e:
                print(f"Update error: {e}")
            time.sleep(1)

    threading.Thread(target=monitoring_loop, daemon=True).start()

if __name__ == "__main__":
    # Use flet.app(target=main) or flet.run(main) if available
    ft.app(target=main)
