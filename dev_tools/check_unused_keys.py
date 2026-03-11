import os
import json
import xml.etree.ElementTree as ET
import re
import urllib.request

BRANCH = "Omega"
KEYBOARD_XML_URL = f"https://raw.githubusercontent.com/xbmc/xbmc/refs/heads/{BRANCH}/system/keymaps/keyboard.xml"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_JSON = os.path.join(os.path.dirname(SCRIPT_DIR), "data", "keyboard_mapping.json")

def main():
    # 1. 读取 Kodi 所有支持的键盘按键字典
    with open(KEY_JSON, "r", encoding="utf-8") as f:
        mapping = json.load(f)["name_to_code"]
    all_kodi_keys = set(mapping.keys())

    # 2. 通过 GitHub URL 读取 Kodi 官方默认的 keyboard.xml 中已经绑定的按键
    print(f"正在从 GitHub [{BRANCH}] 分支拉取官方 keyboard.xml...\n")
    with urllib.request.urlopen(KEYBOARD_XML_URL) as response:
        xml_data = response.read()

    used_keys = set()
    root = ET.fromstring(xml_data)
    
    # 解析 <keyboard> 节点下的所有键
    for keyboard_node in root.iter("keyboard"):
        for key_node in keyboard_node:
            used_keys.add(key_node.tag.lower())

    # 3. 按照映射背后的数字 ID 来判断是否被占用
    # （解决按键“别名”问题，比如 escape 和 esc 在 Kodi 底层指向同一个数字 ID）
    used_codes = set()
    for k in used_keys:
        if k in mapping:
            used_codes.add(mapping[k])

    unused_keys = set()
    for k, code in mapping.items():
        if code not in used_codes:
            unused_keys.add(k)
    
    # 4. 我们只关心“标准电脑键盘”上的按键 (过滤掉各种特殊的多媒体控制键)
    standard_keys_set = {
        # 字母
        'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
        # 数字
        'zero','one','two','three','four','five','six','seven','eight','nine',
        # F区
        'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','f13','f14','f15',
        # 控制与导航
        'escape','esc','tab','return','enter','space','backspace','insert','delete','home','end','pageup','pagedown',
        'up','down','left','right',
        # 符号
        'minus','plus','equals','comma','period','forwardslash','backslash','leftbracket','rightbracket',
        'semicolon','quote','tilde','colon','lessthan','greaterthan','questionmark','at','pipe','caret','underline',
        # 数字小键盘
        'numpadzero','numpadone','numpadtwo','numpadthree','numpadfour','numpadfive','numpadsix','numpadseven',
        'numpadeight','numpadnine','numpaddivide','numpadtimes','numpadminus','numpadplus','numpadperiod',
        # 系统修饰键
        'capslock','numlock','scrolllock','printscreen','pause',
        'leftshift','rightshift','leftctrl','rightctrl','leftalt','rightalt','leftwindows','rightwindows'
    }

    standard_unused = [k for k in unused_keys if k in standard_keys_set]
    
    # 5. 分类输出结果以便阅读
    def group_key(k):
        if len(k) == 1 and k.isalpha(): return "字母 (Letters)"
        if k in ['zero','one','two','three','four','five','six','seven','eight','nine']: return "数字 (Numbers)"
        if re.match(r'^f\d+$', k): return "F 功能键 (Function Keys)"
        if k.startswith('numpad'): return "数字小键盘 (Numpad)"
        if k in ['minus','plus','equals','comma','period','forwardslash','backslash','leftbracket','rightbracket','semicolon','quote','tilde','colon','lessthan','greaterthan','questionmark','at','pipe','caret','underline']: return "标点符号 (Punctuation)"
        return "控制/系统键/修饰键 (Control/Mod Keys)"

    grouped = {}
    for k in standard_unused:
        g = group_key(k)
        grouped.setdefault(g, []).append(k)

    print("=== Kodi 官方 keyboard.xml 未使用的标准键盘按键检测 ===\n")
    for g, keys in sorted(grouped.items()):
        print(f"[{g}] - 共 {len(keys)} 个")
        # 排序输出让找起来更方便
        print("  " + ", ".join(sorted(keys)))
        print("")

if __name__ == "__main__":
    main()
