import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure the project root is in the path
sys.path.append(os.getcwd())

from core.tools import LinuxHands, WindowsHands, AndroidHands

class TestUniversalHands(unittest.TestCase):
    """
    Validation suite to ensure all platform-specific 'Hands' are 
    structurally sound and logically complete.
    """

    def setUp(self):
        # We mock dependencies like psutil and subprocess for cross-platform unit testing
        self.mock_psutil_bat = patch('psutil.sensors_battery').start()
        self.mock_subprocess = patch('subprocess.run').start()
        self.mock_shutil = patch('shutil.which').start()

    def tearDown(self):
        patch.stopall()

    def test_abstract_method_completeness(self):
        """Verify that all subclasses implement the full BaseHands interface."""
        capabilities = [
            "execute_shell", "get_existence_stats", "get_physical_state",
            "get_system_stats", "read_active_window", "ocr_screen",
            "get_process_list", "suspend_process", "resume_process",
            "check_zombies", "get_gpu_stats", "power_control",
            "get_startup_items", "manage_service", "control_network",
            "observe_ui_tree", "get_network_stats", "list_dir",
            "capture_screen", "gui_click", "gui_type", "gui_scroll",
            "gui_speak", "stop_speaking"
        ]
        
        platforms = [LinuxHands, WindowsHands, AndroidHands]
        
        for platform_class in platforms:
            instance = platform_class()
            for cap in capabilities:
                # We check if the method exists
                self.assertTrue(hasattr(instance, cap), f"Platform {platform_class.__name__} is missing capability: {cap}")
                method = getattr(instance, cap)
                self.assertTrue(callable(method), f"Capability {cap} in {platform_class.__name__} is not callable")

    def test_windows_powershell_syntax(self):
        """Verify that WindowsHands generates valid PowerShell scripts for critical tasks."""
        win = WindowsHands()
        
        # Test Active Window Sensing Script
        with patch.object(win, 'execute_shell') as mock_shell:
            mock_shell.return_value = {"exit_code": 0, "output": "VS Code"}
            val = win.read_active_window()
            # Get the argument passed to execute_shell
            args, _ = mock_shell.call_args
            script = args[0]
            self.assertIn("user32.dll", script)
            self.assertIn("GetForegroundWindow", script)
            self.assertIn("Add-Type", script)
            self.assertEqual(val, "VS Code")

        # Test GUI Click Script
        with patch.object(win, 'execute_shell') as mock_shell:
            win.gui_click(100, 200)
            args, _ = mock_shell.call_args
            script = args[0]
            self.assertIn("SetCursorPos(100, 200)", script)
            self.assertIn("mouse_event(0x0002", script) # Left Down

    def test_android_termux_api_mapping(self):
        """Verify that AndroidHands correctly maps actions to Termux-API or Root commands."""
        android = AndroidHands()
        
        # Test WiFi control
        self.mock_shutil.return_value = "/usr/bin/termux-wifi-enable"
        with patch('subprocess.run') as mock_run:
            android.control_network("wlan0", "up")
            args, _ = mock_run.call_args
            cmd = args[0]
            self.assertIn("termux-wifi-enable true", cmd)

        # Test Root GUI Input
        with patch.object(android, 'execute_shell') as mock_shell:
            android.gui_click(500, 500)
            args, _ = mock_shell.call_args
            cmd = args[0]
            self.assertIn("su -c input tap 500 500", cmd)

    def test_linux_x11_parity(self):
        """Verify that LinuxHands maintains its core X11 capabilities."""
        linux = LinuxHands()
        
        # Test Active Window (xprop)
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock()
            mock_run.return_value.stdout = "_NET_ACTIVE_WINDOW(WINDOW): window id # 0x12345"
            linux.read_active_window()
            # First call is to Get root active window id
            self.assertGreaterEqual(mock_run.call_count, 1)

if __name__ == "__main__":
    unittest.main()
