# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcvfs
import threading
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

def log(msg, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_ID}] {msg}", level)

class CustomSelectDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(CustomSelectDialog, self).__init__(*args, **kwargs)
        self.dialog_title = ""
        self.items = []
        self.preselect_index = 0
        self.result = -1
        self.back_id = -1
        self.exit_id = -1
        self.extra_id = -1
        self.extra_button = None

    def set_items(self, title, items, preselect=0, extra_button=None, show_back=True):
        self.dialog_title = title
        self.items = items
        self.preselect_index = max(0, preselect) # 防御性编程
        self.extra_button = extra_button
        self.show_back = show_back

    def onInit(self):
        try:
            self.getControl(1).setLabel(self.dialog_title)
        except Exception:
            pass
            
        available_buttons = []
        # 避免大范围遍历引起日志报错，只测试常见的无异常按钮ID（Estuary 皮肤一般是 5, 7, 8）
        for i in (5, 7, 8):
            try:
                control = self.getControl(i)
                if isinstance(control, xbmcgui.ControlButton):
                    available_buttons.append(control)
            except Exception:
                pass
                
        # 按需分配按钮：附加按钮（如映射编辑器），其次为返回（可选），然后是退出
        btn_idx = 0
        
        if len(available_buttons) > btn_idx and getattr(self, 'extra_button', None):
            self.extra_id = available_buttons[btn_idx].getId()
            try:
                available_buttons[btn_idx].setVisible(True)
                available_buttons[btn_idx].setLabel(self.extra_button)
            except Exception: pass
            btn_idx += 1
            
        if len(available_buttons) > btn_idx and getattr(self, 'show_back', True):
            self.back_id = available_buttons[btn_idx].getId()
            try:
                available_buttons[btn_idx].setVisible(True)
                available_buttons[btn_idx].setLabel("返回")
            except Exception: pass
            btn_idx += 1

        if len(available_buttons) > btn_idx:
            self.exit_id = available_buttons[btn_idx].getId()
            try:
                available_buttons[btn_idx].setVisible(True)
                available_buttons[btn_idx].setLabel("退出")
            except Exception: pass
            btn_idx += 1

        # 隐藏多余的按钮
        for btn in available_buttons[btn_idx:]:
            try:
                btn.setVisible(False)
            except Exception: pass
            
        # 自动探测是否需要显示图标
        has_icons = any(isinstance(item, dict) and item.get('icon') for item in self.items)
        # 具有图标时首选列表6（图文宽列表），没有图标时首选列表3（纯文本紧凑列表）
        target_list_ids = (6, 3) if has_icons else (3, 6)

        self.list_control = None
        for control_id in target_list_ids:
            try:
                control = self.getControl(control_id)
                if isinstance(control, xbmcgui.ControlList):
                    if self.list_control is None:
                        self.list_control = control
                        control.setVisible(True)
                    else:
                        # 隐藏掉不需要的另一个列表，防止重叠
                        control.setVisible(False)
            except Exception:
                continue

        if self.list_control is None:
            return

        for item_data in self.items:
            if isinstance(item_data, dict):
                list_item = xbmcgui.ListItem(item_data.get('label', ''))
                icon = item_data.get('icon')
                if icon:
                    list_item.setArt({'icon': icon, 'thumb': icon})
            else:
                list_item = xbmcgui.ListItem(str(item_data))
            self.list_control.addItem(list_item)

        self.setFocus(self.list_control)
        if 0 <= self.preselect_index < self.list_control.size():
            self.list_control.selectItem(self.preselect_index)

    def onClick(self, controlId):
        xbmc.log(f"[RemoteSwitcher] onClick triggered with controlId: {controlId}", xbmc.LOGINFO)
        if controlId in (6, 3):
            self.result = self.list_control.getSelectedPosition()
        elif getattr(self, 'extra_id', -1) != -1 and controlId == self.extra_id:
            self.result = -3
        elif controlId == self.exit_id:
            self.result = -2
        elif controlId == self.back_id:
            self.result = -1
        else:
            self.result = -1
        self.close()

    def onAction(self, action):
        log(f"onAction triggered with action-------: {action}", xbmc.LOGINFO)
        action_id = action.getId()
        # 92(back), 10(esc)
        if action_id in (92, 10):
            self.result = -1
            self.close()
        # 122(home键) 等价于点击了退出按钮 (-2) 并打开主页
        elif action_id == 122:
            self.result = -2
            self.close()
            xbmc.executebuiltin('ActivateWindow(home)')
        elif action_id in (7, 100):
            try:
                focus_id = self.getFocusId()
                if self.list_control is not None and focus_id == self.list_control.getId():
                    self.result = self.list_control.getSelectedPosition()
                    self.close()
            except Exception:
                pass

def custom_select(title, items, preselect=0, extra_button=None, show_back=True):
    import sys
    dialog = CustomSelectDialog("CustomDialogSelect.xml", ADDON_PATH, "default", "1080i")
    dialog.set_items(title, items, preselect, extra_button, show_back)
    dialog.doModal()
    result = dialog.result
    del dialog
    if result == -2:
        sys.exit(0) # 彻底退出整个 addon
    return result

class CustomTextViewerDialog(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(CustomTextViewerDialog, self).__init__(*args, **kwargs)
        self.dialog_title = ""
        self.text = ""

    def set_content(self, title, text):
        self.dialog_title = title
        self.text = text

    def onInit(self):
        try:
            self.getControl(1).setLabel(self.dialog_title)
        except Exception:
            pass
        try:
            self.getControl(5).setText(self.text)
        except Exception:
            pass

    def onAction(self, action):
        action_id = action.getId()
        if action_id in (92, 10):
            self.close()
        elif action_id in (3, 5):  # ACTION_MOVE_UP, ACTION_PAGE_UP
            xbmc.executebuiltin('PageUp(61)')
        elif action_id in (4, 6):  # ACTION_MOVE_DOWN, ACTION_PAGE_DOWN
            xbmc.executebuiltin('PageDown(61)')

def custom_textviewer(title, text):
    dialog = CustomTextViewerDialog("CustomDialogTextViewer.xml", ADDON_PATH, "default", "1080i")
    dialog.set_content(title, text)
    dialog.doModal()
    del dialog


class CustomConfirmDialog(xbmcgui.WindowXMLDialog):
    RESULT_CANCELLED = -1
    RESULT_NO = 0
    RESULT_YES = 1
    RESULT_CUSTOM = 2

    def __init__(self, *args, **kwargs):
        super(CustomConfirmDialog, self).__init__(*args, **kwargs)
        self.dialog_title = ""
        self.text = ""
        self.no_label = ""
        self.yes_label = ""
        self.custom_label = ""
        self.default_button = 11
        self.result = self.RESULT_CANCELLED

    def set_content(self, title, text, no_label="否", yes_label="是",
                    custom_label="", default_button=11):
        self.dialog_title = title
        self.text = text
        self.no_label = no_label
        self.yes_label = yes_label
        self.custom_label = custom_label
        self.default_button = default_button

    def onInit(self):
        try:
            self.getControl(1).setLabel(self.dialog_title)
        except Exception:
            pass
        try:
            self.getControl(9).setText(self.text)
        except Exception:
            pass

        # 按钮10=No, 11=Yes, 12=Custom
        try:
            btn_no = self.getControl(10)
            btn_no.setLabel(self.no_label)
        except Exception:
            pass
        try:
            btn_yes = self.getControl(11)
            btn_yes.setLabel(self.yes_label)
        except Exception:
            pass
        try:
            btn_custom = self.getControl(12)
            if self.custom_label:
                btn_custom.setLabel(self.custom_label)
                btn_custom.setVisible(True)
            else:
                btn_custom.setVisible(False)
        except Exception:
            pass

        try:
            self.setFocusId(self.default_button)
        except Exception:
            pass

    def onClick(self, controlId):
        if controlId == 10:
            self.result = self.RESULT_NO
        elif controlId == 11:
            self.result = self.RESULT_YES
        elif controlId == 12:
            self.result = self.RESULT_CUSTOM
        self.close()

    def onAction(self, action):
        if action.getId() in (92, 10):
            self.result = self.RESULT_CANCELLED
            self.close()


def custom_confirm(title, text, no_label="否", yes_label="是",
                   custom_label="", default_button=11):
    """自定义确认弹窗，返回 RESULT_YES/RESULT_NO/RESULT_CUSTOM/RESULT_CANCELLED"""
    dialog = CustomConfirmDialog("CustomDialogConfirm.xml", ADDON_PATH, "default", "1080i")
    dialog.set_content(title, text, no_label, yes_label, custom_label, default_button)
    dialog.doModal()
    result = dialog.result
    del dialog
    return result

def sync_reload_keymaps():
    # 使用同步等待方案：Python 插件在独立线程运行，它的 sleep 不会卡住 Kodi 自身的 UI 动画。
    # 我们故意让插件暂停 400ms，让上一个菜单的关闭动画彻底播放完毕，
    # 然后安全调用重载，之后再打开下一个菜单。
    xbmc.sleep(400)
    xbmc.executebuiltin('Action(ReloadKeymaps)')
    xbmc.log('[RemoteSwitcher] Keymaps reloaded successfully.', xbmc.LOGINFO)
