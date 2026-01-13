"""
Umbrasol Flet GUI Application
Simplified version compatible with Flet 0.80.1
"""
import flet as ft
import sys
import os
from threading import Thread

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.umbrasol import UmbrasolCore


class UmbrasolApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.agent = UmbrasolCore(voice_mode=False)
        
        # Configure page
        self.page.title = "Umbrasol Intelligence"
        self.page.theme_mode = "dark"
        self.page.padding = 20
        self.page.window_width = 1000
        self.page.window_height = 700
        
        # Initialize UI
        self.setup_ui()
        
    def setup_ui(self):
        """Build the UI"""
        
        # Header
        header = ft.Text(
            "Umbrasol Intelligence v12.1",
            size=24,
            weight="bold",
            color="#6366f1"
        )
        
        platform_info = ft.Text(
            f"Platform: {sys.platform.upper()}",
            size=12,
            color="#9ca3af"
        )
        
        # Chat area
        self.chat_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=10,
            auto_scroll=True,
        )
        
        # Welcome message
        self.add_system_message("System ready. Type your command below.")
        
        # Input
        self.input_field = ft.TextField(
            hint_text="Type your command here...",
            multiline=False,
            on_submit=self.send_message,
            border_color="#6366f1",
            text_size=14,
        )
        
        send_button = ft.ElevatedButton(
            "Send",
            on_click=self.send_message,
            bgcolor="#6366f1",
            color="#ffffff",
        )
        
        # Layout
        self.page.add(
            ft.Column(
                [
                    header,
                    platform_info,
                    ft.Divider(height=20, color="#ffffff1a"),
                    ft.Container(
                        content=self.chat_list,
                        expand=True,
                        bgcolor="#00000033",
                        padding=10,
                        border_radius=10,
                    ),
                    ft.Row(
                        [self.input_field, send_button],
                        spacing=10,
                    ),
                ],
                expand=True,
                spacing=10,
            )
        )
        
        self.input_field.focus()
    
    def add_user_message(self, text: str):
        """Add user message"""
        msg = ft.Container(
            content=ft.Column([
                ft.Text("You:", size=11, weight="bold", color="#9ca3af"),
                ft.Text(text, size=13, color="#ffffff"),
            ], spacing=2),
            bgcolor="#6366f11a",
            padding=10,
            border_radius=8,
        )
        self.chat_list.controls.append(msg)
        self.page.update()
    
    def add_agent_message(self, text: str):
        """Add agent message"""
        msg = ft.Container(
            content=ft.Column([
                ft.Text("Umbrasol:", size=11, weight="bold", color="#6366f1"),
                ft.Text(text, size=13, color="#e5e7eb"),
            ], spacing=2),
            bgcolor="#ffffff0d",
            padding=10,
            border_radius=8,
        )
        self.chat_list.controls.append(msg)
        self.page.update()
    
    def add_system_message(self, text: str):
        """Add system message"""
        msg = ft.Text(text, size=11, color="#6b7280", italic=True)
        self.chat_list.controls.append(msg)
        self.page.update()
    
    def add_thinking(self):
        """Add thinking indicator"""
        self.thinking = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=14, height=14, stroke_width=2),
                ft.Text("Processing...", size=11, color="#6366f1"),
            ], spacing=8),
            padding=8,
        )
        self.chat_list.controls.append(self.thinking)
        self.page.update()
    
    def remove_thinking(self):
        """Remove thinking indicator"""
        if hasattr(self, 'thinking'):
            try:
                self.chat_list.controls.remove(self.thinking)
                self.page.update()
            except:
                pass
    
    def send_message(self, e):
        """Send message"""
        text = self.input_field.value.strip()
        if not text:
            return
        
        self.add_user_message(text)
        self.input_field.value = ""
        self.page.update()
        
        def process():
            self.add_thinking()
            try:
                response = self.agent.execute(text)
                self.remove_thinking()
                self.add_agent_message(response if response else "Done.")
            except Exception as ex:
                self.remove_thinking()
                self.add_system_message(f"Error: {str(ex)}")
        
        Thread(target=process, daemon=True).start()


def main(page: ft.Page):
    UmbrasolApp(page)


if __name__ == "__main__":
    ft.app(target=main)
