"""
Umbrasol Flet GUI Application
Modern cross-platform interface using Flet (Flutter in Python)
"""
import flet as ft
import sys
import os
from threading import Thread
from queue import Queue

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.umbrasol import UmbrasolCore


class UmbrasolApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.agent = UmbrasolCore(voice_mode=False)
        self.message_queue = Queue()
        
        # Configure page
        self.page.title = "Umbrasol Intelligence"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # Custom dark theme
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.INDIGO,
            use_material3=True,
        )
        
        # Initialize UI components
        self.setup_ui()
        
    def setup_ui(self):
        """Build the main UI layout"""
        
        # Header
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.PSYCHOLOGY, color=ft.colors.INDIGO_400, size=32),
                    ft.Column(
                        [
                            ft.Text("Umbrasol", size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("v12.1 Neural Intelligence", size=11, color=ft.colors.GREY_500),
                        ],
                        spacing=2,
                    ),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.COMPUTER, size=16, color=ft.colors.GREY_600),
                                ft.Text(sys.platform.upper(), size=12, color=ft.colors.GREY_400),
                            ],
                            spacing=8,
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                        bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE),
                        border_radius=20,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=20,
            bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.WHITE))),
        )
        
        # Chat messages list
        self.chat_list = ft.ListView(
            expand=True,
            spacing=16,
            padding=20,
            auto_scroll=True,
        )
        
        # Add welcome message
        self.add_system_message("Umbrasol Intelligence is active. All platform modules verified and ready.")
        
        # Input field
        self.input_field = ft.TextField(
            hint_text="Describe your intent or give a command...",
            border_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
            focused_border_color=ft.colors.INDIGO_400,
            multiline=False,
            on_submit=self.send_message,
            expand=True,
            text_size=14,
            bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE),
            border_radius=12,
        )
        
        # Send button
        send_btn = ft.IconButton(
            icon=ft.icons.ARROW_UPWARD_ROUNDED,
            icon_color=ft.colors.BLACK,
            bgcolor=ft.colors.WHITE,
            on_click=self.send_message,
            tooltip="Send message",
        )
        
        # Input container
        input_container = ft.Container(
            content=ft.Row(
                [
                    self.input_field,
                    send_btn,
                ],
                spacing=12,
            ),
            padding=20,
            bgcolor=ft.colors.with_opacity(0.02, ft.colors.WHITE),
            border=ft.border.only(top=ft.BorderSide(1, ft.colors.with_opacity(0.1, ft.colors.WHITE))),
        )
        
        # Main layout
        self.page.add(
            ft.Column(
                [
                    header,
                    ft.Container(
                        content=self.chat_list,
                        expand=True,
                        bgcolor=ft.colors.with_opacity(0.01, ft.colors.WHITE),
                    ),
                    input_container,
                ],
                spacing=0,
                expand=True,
            )
        )
        
        # Focus input field
        self.input_field.focus()
    
    def add_user_message(self, text: str):
        """Add user message to chat"""
        message = ft.Container(
            content=ft.Column(
                [
                    ft.Text("You", size=11, weight=ft.FontWeight.BOLD, color=ft.colors.GREY_500),
                    ft.Text(text, size=14, color=ft.colors.WHITE),
                ],
                spacing=4,
            ),
            padding=16,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.INDIGO),
            border_radius=12,
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.INDIGO)),
        )
        self.chat_list.controls.append(message)
        self.page.update()
    
    def add_agent_message(self, text: str):
        """Add agent response to chat"""
        message = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Umbrasol", size=11, weight=ft.FontWeight.BOLD, color=ft.colors.INDIGO_400),
                    ft.Text(text, size=14, color=ft.colors.GREY_200),
                ],
                spacing=4,
            ),
            padding=16,
            bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE),
            border_radius=12,
            border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.WHITE)),
        )
        self.chat_list.controls.append(message)
        self.page.update()
    
    def add_system_message(self, text: str):
        """Add system message to chat"""
        message = ft.Container(
            content=ft.Text(text, size=12, color=ft.colors.GREY_600, italic=True),
            padding=12,
        )
        self.chat_list.controls.append(message)
        self.page.update()
    
    def add_thinking_indicator(self):
        """Add thinking indicator"""
        self.thinking = ft.Container(
            content=ft.Row(
                [
                    ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.colors.INDIGO_400),
                    ft.Text("Processing...", size=12, color=ft.colors.INDIGO_400),
                ],
                spacing=8,
            ),
            padding=12,
        )
        self.chat_list.controls.append(self.thinking)
        self.page.update()
    
    def remove_thinking_indicator(self):
        """Remove thinking indicator"""
        if hasattr(self, 'thinking') and self.thinking in self.chat_list.controls:
            self.chat_list.controls.remove(self.thinking)
            self.page.update()
    
    def send_message(self, e):
        """Handle message send"""
        text = self.input_field.value.strip()
        if not text:
            return
        
        # Add user message
        self.add_user_message(text)
        self.input_field.value = ""
        self.page.update()
        
        # Process in background thread
        def process():
            self.add_thinking_indicator()
            try:
                # Execute command through Umbrasol
                response = self.agent.execute(text)
                self.remove_thinking_indicator()
                self.add_agent_message(response if response else "Task completed.")
            except Exception as ex:
                self.remove_thinking_indicator()
                self.add_system_message(f"Error: {str(ex)}")
        
        Thread(target=process, daemon=True).start()


def main(page: ft.Page):
    """Main entry point for Flet app"""
    UmbrasolApp(page)


if __name__ == "__main__":
    ft.app(target=main)
