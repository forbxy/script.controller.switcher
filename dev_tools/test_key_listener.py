"""Run outside Kodi: python3 -m unittest discover -s dev_tools -p 'test_*.py'."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


class Label:
    def __init__(self):
        self.history = []

    def setLabel(self, text):
        self.history.append(text)


class FadeLabel:
    def __init__(self):
        self.labels = ["旧内容"]
        self.history = []

    def reset(self):
        self.labels.clear()

    def addLabel(self, text):
        self.labels.append(text)
        self.history.append(text)


class WindowXMLDialog:
    def __new__(cls, *args):
        return object.__new__(cls)


def load_keymap_module():
    xbmc = ModuleType("xbmc")
    xbmc.LOGWARNING = 2
    xbmc.sleep = Mock()
    xbmcgui = ModuleType("xbmcgui")
    xbmcgui.WindowXMLDialog = WindowXMLDialog
    xbmcgui.ControlFadeLabel = FadeLabel
    xbmcaddon = ModuleType("xbmcaddon")
    xbmcaddon.Addon = Mock(return_value=SimpleNamespace(
        getAddonInfo=lambda key: "5.17.0" if key == "version" else "test"))
    xbmcvfs = ModuleType("xbmcvfs")
    xbmcvfs.translatePath = lambda path: path
    utils = ModuleType("utils")
    for name in ("custom_select", "log", "sync_reload_keymaps",
                 "custom_confirm", "CustomConfirmDialog"):
        setattr(utils, name, Mock())
    source = Path(__file__).resolve().parents[1] / "custom_keymap.py"
    spec = importlib.util.spec_from_file_location("keymap_under_test", source)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, xbmc=xbmc, xbmcgui=xbmcgui,
                    xbmcaddon=xbmcaddon, xbmcvfs=xbmcvfs, utils=utils):
        spec.loader.exec_module(module)
    return module


class KeyListenerTests(unittest.TestCase):
    def setUp(self):
        self.module = load_keymap_module()
        # Advance the real countdown synchronously with a simulated Kodi clock.
        self.module.Thread = Mock()

    def listener(self, title, countdown):
        dialog = self.module.KeyListener()
        dialog.getControl = Mock(side_effect={401: title, 402: countdown}.__getitem__)
        dialog.close = Mock()
        return dialog

    def test_countdown_and_timeout_with_skin_label_types(self):
        for title_type in (Label, FadeLabel):
            for countdown_type in (Label, FadeLabel):
                with self.subTest(title=title_type, countdown=countdown_type):
                    countdown = countdown_type()
                    dialog = self.listener(title_type(), countdown)
                    dialog.onInit()
                    dialog._countdown()
                    self.assertEqual(countdown.history,
                                     [f"{n} 秒后超时" for n in range(5, 0, -1)])
                    if isinstance(countdown, FadeLabel):
                        self.assertEqual(countdown.labels, ["1 秒后超时"])
                    self.assertIsNone(dialog.key)
                    dialog.close.assert_called_once()

    def test_failed_label_update_still_times_out(self):
        countdown = Label()
        countdown.setLabel = Mock(side_effect=RuntimeError("控件失效"))
        dialog = self.listener(Label(), countdown)
        dialog.onInit()
        dialog._countdown()
        self.assertEqual(self.module.xbmc.sleep.call_count, 5)
        self.assertEqual(self.module.log.call_count, 5)
        dialog.close.assert_called_once()

    def test_missing_skin_controls_still_times_out(self):
        dialog = self.listener(Label(), Label())
        dialog.getControl.side_effect = RuntimeError("皮肤控件不存在")
        dialog.onInit()
        dialog._countdown()
        self.assertIsNone(dialog.key)
        dialog.close.assert_called_once()

    def test_input_stops_countdown_and_removes_longpress_modifier(self):
        countdown = FadeLabel()
        dialog = self.listener(FadeLabel(), countdown)
        dialog.onInit()
        action = SimpleNamespace(getButtonCode=lambda: 0x01000000 | 61527)
        self.module.xbmc.sleep.side_effect = lambda _: dialog.onAction(action)
        dialog._countdown()
        self.assertEqual(dialog.key, "61527")
        self.assertEqual(countdown.history, ["5 秒后超时"])
        dialog.close.assert_called_once()

    def test_action_without_button_code_does_not_prevent_timeout(self):
        dialog = self.listener(Label(), Label())
        dialog.onInit()
        action = SimpleNamespace(getButtonCode=lambda: 0)
        self.module.xbmc.sleep.side_effect = lambda _: dialog.onAction(action)
        dialog._countdown()
        self.assertIsNone(dialog.key)
        dialog.close.assert_called_once()

    def test_one_second_timeout(self):
        dialog = self.listener(Label(), FadeLabel())
        dialog.TIMEOUT = 1
        dialog.onInit()
        dialog._countdown()
        self.module.xbmc.sleep.assert_called_once_with(1000)
        dialog.close.assert_called_once()

    def test_modal_exit_stops_countdown_even_on_error(self):
        # Cover a window dismissed externally, including an unexpected modal error.
        for error in (None, RuntimeError("窗口已关闭")):
            with self.subTest(error=error):
                dialog = self.listener(Label(), Label())
                dialog._countdown_active = True
                dialog.doModal = Mock(side_effect=error)
                with patch.object(self.module, "KeyListener", return_value=dialog):
                    record_key = type(dialog).record_key
                    if error:
                        with self.assertRaises(RuntimeError):
                            record_key()
                    else:
                        self.assertIsNone(record_key())
                self.assertFalse(dialog._countdown_active)


if __name__ == "__main__":
    unittest.main()
