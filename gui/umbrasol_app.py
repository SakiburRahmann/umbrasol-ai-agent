"""
Umbrasol Flet GUI Application v12.2
Premium Dark Theme | Streaming AI | Markdown Support
Compatible with Flet 0.80.1
"""
import flet as ft
import sys
import os
import time
import psutil
from threading import Thread

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.umbrasol import UmbrasolCore

# --- THEME CONSTANTS ---
BG_COLOR = "#0F172A"       # Slate 900
SURFACE_COLOR = "#1E293B"  # Slate 800
ACCENT_COLOR = "#6366F1"   # Indigo 500
TEXT_MAIN = "#F8FAFC"      # Slate 50
TEXT_MUTED = "#94A3B8"     # Slate 400
USER_BUBBLE = "#3730A3"    # Indigo 800
AGENT_BUBBLE = "#334155"   # Slate 700
BORDER_COLOR = "#334155"   # Slate 700

class UmbrasolApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.agent = UmbrasolCore(voice_mode=False)
        
        # Configure page basics
        self.page.title = "Umbrasol Intelligence"
        self.page.theme_mode = "dark"
        self.page.padding = 0
        self.page.bgcolor = BG_COLOR
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # UI State
        self.memory_usage = ft.Text("RAM: --%", size=11, color=ACCENT_COLOR, weight="bold")
        self.cpu_usage = ft.Text("CPU: --%", size=11, color=ACCENT_COLOR, weight="bold")
        
        self.setup_ui()
        
        # Start background stats update
        Thread(target=self.update_stats, daemon=True).start()
        
    def setup_ui(self):
        """Build the Premium UI"""
        
        # --- HEADER ---
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Row([
                        ft.Icon("token", color=ACCENT_COLOR, size=24), # Generic token icon replaces specific abstract ones
                        ft.Column([
                            ft.Text("UMBRASOL", size=14, weight="bold", color=TEXT_MAIN, letter_spacing=2),
                            ft.Text("NEURAL INTERFACE v12.2", size=10, color=TEXT_MUTED),
                        ], spacing=0)
                    ], spacing=12),
                    
                    ft.Container(expand=True),
                    
                    # Telemetry
                    ft.Container(
                        content=ft.Row([
                            ft.Icon("memory", size=14, color=TEXT_MUTED),
                            self.memory_usage,
                            ft.Container(width=10),
                            ft.Icon("computer", size=14, color=TEXT_MUTED),
                            self.cpu_usage,
                        ]),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        bgcolor=SURFACE_COLOR,
                        border_radius=20,
                        border=ft.border.all(1, BORDER_COLOR)
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            bgcolor=BG_COLOR,
            border=ft.border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
        )

        # --- CHAT AREA ---
        self.chat_list = ft.ListView(
            expand=True,
            spacing=24,
            padding=24,
            auto_scroll=True,
        )
        
        # --- INPUT AREA ---
        self.input_field = ft.TextField(
            hint_text="Type your directive...",
            hint_style=ft.TextStyle(color=TEXT_MUTED),
            text_style=ft.TextStyle(color=TEXT_MAIN, size=14),
            multiline=False,
            on_submit=self.send_message,
            expand=True,
            border_color="transparent",
            bgcolor="transparent",
            content_padding=16,
            cursor_color=ACCENT_COLOR,
        )
        
        send_btn = ft.Container(
            content=ft.Icon("arrow_upward", color=TEXT_MAIN, size=20),
            width=40,
            height=40,
            bgcolor=ACCENT_COLOR,
            border_radius=12,
            alignment=ft.alignment.center,
            on_click=self.send_message,
            animate=ft.animation.Animation(200, "easeOut"),
        )

        input_container = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=self.input_field,
                    expand=True,
                    bgcolor=SURFACE_COLOR,
                    border_radius=12,
                    border=ft.border.all(1, BORDER_COLOR),
                ),
                send_btn
            ], spacing=12),
            padding=24,
            bgcolor=BG_COLOR,
            border=ft.border.only(top=ft.BorderSide(1, BORDER_COLOR)),
        )

        # --- ASSEMBLY ---
        self.page.add(
            ft.Column(
                [
                    header,
                    ft.Container(content=self.chat_list, expand=True, bgcolor=BG_COLOR),
                    input_container
                ],
                spacing=0,
                expand=True
            )
        )
        
        # Welcome
        self.add_system_message("System Initialized. Ready for input.")
        self.input_field.focus()

    def update_stats(self):
        """Background thread to update telemetry"""
        while True:
            try:
                mem = psutil.virtual_memory().percent
                cpu = psutil.cpu_percent(interval=None)
                self.memory_usage.value = f"RAM: {mem}%"
                self.cpu_usage.value = f"CPU: {cpu}%"
                self.page.update()
                time.sleep(2)
            except:
                break

    def add_user_message(self, text: str):
        """Right-aligned user bubble"""
        msg = ft.Row([
            ft.Container(expand=True), # Spacer for right align
            ft.Container(
                content=ft.Text(text, color=TEXT_MAIN, size=14),
                bgcolor=USER_BUBBLE,
                padding=16,
                border_radius=ft.border_radius.only(20, 20, 4, 20),
                constraints=ft.BoxConstraints(max_width=800),
            ),
            ft.Container(
                content=ft.Icon("person", color=TEXT_MUTED, size=24),
                alignment=ft.alignment.top_center,
                padding=ft.padding.only(top=8)
            )
        ], alignment=ft.MainAxisAlignment.END, spacing=12)
        
        self.chat_list.controls.append(msg)
        self.page.update()

    def add_system_message(self, text: str):
        """Centered system notification"""
        msg = ft.Row([
            ft.Container(
                content=ft.Text(text, color=TEXT_MUTED, size=11, italic=True),
                padding=8,
                bgcolor=SURFACE_COLOR,
                border_radius=12,
            )
        ], alignment=ft.MainAxisAlignment.CENTER)
        self.chat_list.controls.append(msg)
        self.page.update()

    def add_agent_message_placeholder(self):
        """Left-aligned agent bubble (placeholder)"""
        # We use a Markdown control for rich text
        md_control = ft.Markdown(
            "",
            selectable=True,
            extension_set="github_web",
            code_theme="atom-one-dark",
            on_tap_link=lambda e: self.page.launch_url(e.data),
        )
        
        msg = ft.Row([
            ft.Container(
                content=ft.Icon("smart_toy", color=ACCENT_COLOR, size=24),
                alignment=ft.alignment.top_center,
                padding=ft.padding.only(top=8)
            ),
            ft.Container(
                content=md_control,
                bgcolor=AGENT_BUBBLE,
                padding=16,
                border_radius=ft.border_radius.only(20, 20, 20, 4),
                constraints=ft.BoxConstraints(max_width=800),
            ),
            ft.Container(expand=True) # Spacer for left align
        ], alignment=ft.MainAxisAlignment.START, spacing=12)
        
        self.chat_list.controls.append(msg)
        self.page.update()
        return md_control

    def send_message(self, e):
        """Handle send event"""
        text = self.input_field.value.strip()
        if not text: return
        
        self.input_field.value = ""
        self.add_user_message(text)
        
        # Create placeholder for streaming response
        response_md_control = self.add_agent_message_placeholder()
        
        def process():
            current_text = ""
            
            def on_token(token):
                nonlocal current_text
                current_text += token
                response_md_control.value = current_text
                self.page.update()
                
            try:
                # Add "Thinking..." temporary state if needed, or just start
                self.agent.execute(text, on_token=on_token)
                
                if not current_text:
                    response_md_control.value = "_Task completed successfully._"
                    self.page.update()
                    
            except Exception as ex:
                response_md_control.value = f"**Error executing task:** {str(ex)}"
                self.page.update()
        
        Thread(target=process, daemon=True).start()

def main(page: ft.Page):
    UmbrasolApp(page)

if __name__ == "__main__":
    ft.app(target=main)
