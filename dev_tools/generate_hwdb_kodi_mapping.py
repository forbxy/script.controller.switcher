import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
KEYBOARD_MAPPING_FILE = os.path.join(DATA_DIR, "keyboard_mapping.json")

def generate_hwdb_kodi_mapping():
    """
    生成 linux hwdb (evdev) 的按键名 到 Kodi <keyboard> 标签键名的映射关系
    """
    if not os.path.exists(KEYBOARD_MAPPING_FILE):
        print(f"[{KEYBOARD_MAPPING_FILE}] 不存在，请先运行 generate_keymap_json.py")
        return

    with open(KEYBOARD_MAPPING_FILE, "r", encoding="utf-8") as f:
        kodi_mapping = json.load(f)
        kodi_keys = kodi_mapping.get("name_to_code", {})

    # 手动定义标准 hwdb (来自于 linux input-event-codes.h ) 到 Kodi 键名的映射表
    # 这也是大多数 CoreELEC/LibreELEC 内核默认的转换行为
    hwdb_to_kodi = {
        # 导航键
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
        "enter": "enter",          # KEY_ENTER -> enter
        "ok": "return",            # KEY_OK 有可能被映射为 return 或 enter
        "esc": "escape",
        "escape": "escape",
        "back": "browser_back",    # KEY_BACK -> browser_back (Kodi 中常用返回)
        "homepage": "homepage",    # KEY_HOMEPAGE -> homepage
        "home": "home",            # KEY_HOME -> home
        
        # 菜单与信息
        "compose": "menu",         # KEY_MENU
        "info": "info",            # KEY_INFO
        "epg": "e",                # 电视指南通常映射为 e

        # 媒体控制
        "playpause": "play_pause",
        "play": "play_pause",
        "pause": "pause",
        "stop": "stop",
        "stopcd": "stop",
        "rewind": "rewind",
        "fastforward": "fastforward",
        "nextsong": "next_track",
        "previoussong": "prev_track",
        
        # 音量控制
        "volumeup": "volume_up",
        "volumedown": "volume_down",
        "mute": "volume_mute",
        
        # 系统与频道
        "power": "power",
        "sleep": "sleep",
        "search": "browser_search",
        "channelup": "pageup",
        "channeldown": "pagedown",
        "pageup": "pageup",
        "pagedown": "pagedown",
        
        # 颜色键 (机顶盒遥控器常用)
        "red": "red",
        "green": "green",
        "yellow": "yellow",
        "blue": "blue",
        
        # 数字键
        "0": "zero",
        "1": "one",
        "2": "two",
        "3": "three",
        "4": "four",
        "5": "five",
        "6": "six",
        "7": "seven",
        "8": "eight",
        "9": "nine",
        
        # 其他常见键盘对应
        "space": "space",
        "backspace": "backspace",
        "tab": "tab",
    }

    final_mapping = {}
    missing_kodi_keys = []

    for hwdb_key, kodi_key in hwdb_to_kodi.items():
        if kodi_key in kodi_keys:
            final_mapping[hwdb_key] = kodi_key
        else:
            missing_kodi_keys.append(kodi_key)
            print(f"警告: Kodi 键名 '{kodi_key}' 在 keyboard_mapping.json 中未找到。可能将被忽略。")

    output_path = os.path.join(DATA_DIR, "hwdb_to_kodi.json")
    
    result_data = {
        "description": "Mapping from Linux hwdb (evdev) key names to Kodi keyboard key names",
        "mapping": final_mapping
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)

    print(f"成功生成 JSON 文件: {output_path}")
    print(f"共映射了 {len(final_mapping)} 个按键。")
    if missing_kodi_keys:
        print(f"发现未匹配的 Kodi 键名汇总: {missing_kodi_keys}")

if __name__ == "__main__":
    generate_hwdb_kodi_mapping()