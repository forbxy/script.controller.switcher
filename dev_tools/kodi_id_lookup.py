#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import os

# 源码路径 (由于在你的开发环境中可以直接访问kodi源码)
KEYTABLE_PATH = 'c:/develop/kodi/xbmc/xbmc/input/keyboard/XBMC_keytable.cpp'
VKEYS_PATH = 'c:/develop/kodi/xbmc/xbmc/input/keyboard/XBMC_vkeys.h'
ACTION_IDS_PATH = 'c:/develop/kodi/xbmc/xbmc/input/actions/ActionIDs.h'
ACTION_TRANS_PATH = 'c:/develop/kodi/xbmc/xbmc/input/actions/ActionTranslator.cpp'
IR_TRANS_PATH = 'c:/develop/kodi/xbmc/xbmc/input/keymaps/remote/IRTranslator.cpp'
IR_REMOTE_PATH = 'c:/develop/kodi/xbmc/xbmc/input/remote/IRRemote.h'

def build_keyboard_button_map():
    vkey_values = {}
    if os.path.exists(VKEYS_PATH):
        with open(VKEYS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'(XBMCVK_[A-Z0-9_]+)\s*=\s*(0x[0-9a-fA-F]+|\d+)', line)
                if m: vkey_values[m.group(1)] = int(m.group(2), 0)

    string_to_vkey = {}
    if os.path.exists(KEYTABLE_PATH):
        with open(KEYTABLE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'\{XBMCK_[^,]+,\s*[^,]+,\s*[^,]+,\s*(XBMCVK_[^,]+),\s*"([^"]+)"\}', line)
                if m: string_to_vkey[m.group(2)] = m.group(1)

    KEY_VKEY = 0xF000
    name_to_id = {}
    id_to_names = {}
    for s_name, vk_name in string_to_vkey.items():
        if vk_name in vkey_values:
            full_id = KEY_VKEY | vkey_values[vk_name]
            name_to_id[s_name] = full_id
            id_to_names.setdefault(full_id, []).append(s_name)
    return name_to_id, id_to_names

def build_remote_button_map():
    ir_vals = {}
    if os.path.exists(IR_REMOTE_PATH):
        with open(IR_REMOTE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'#define\s+(XINPUT_IR_REMOTE_[A-Z0-9_]+)\s+([0-9]+|0x[0-9a-fA-F]+)', line)
                if m: ir_vals[m.group(1)] = int(m.group(2), 0)

    name_to_id = {}
    id_to_names = {}
    if os.path.exists(IR_TRANS_PATH):
        with open(IR_TRANS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            # Find all if (strButton == "xxx") buttonCode = XINPUT...
            blocks = re.findall(r'strButton\s*==\s*"([^"]+)"[^{}]+?buttonCode\s*=\s*(XINPUT_IR_REMOTE_[A-Z0-9_]+)', content, re.MULTILINE)
            # fallback if standard regex misses due to formatting
            # Let's do a simple line by line reading state machine
            lines = content.split('\n')
            curr_str = None
            for line in lines:
                m1 = re.search(r'strButton\s*==\s*"([^"]+)"', line)
                if m1: curr_str = m1.group(1)
                m2 = re.search(r'buttonCode\s*=\s*(XINPUT_IR_REMOTE_[A-Z0-9_]+)', line)
                if m2 and curr_str:
                    def_name = m2.group(1)
                    if def_name in ir_vals:
                        val = ir_vals[def_name]
                        name_to_id[curr_str] = val
                        id_to_names.setdefault(val, []).append(curr_str)
                    curr_str = None
                    
    return name_to_id, id_to_names

def build_action_map():
    action_id_values = {}
    if os.path.exists(ACTION_IDS_PATH):
        with open(ACTION_IDS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'constexpr\s+const\s+int\s+([A-Z0-9_]+)\s*=\s*([0-9]+|0x[0-9a-fA-F]+)', line)
                if m: action_id_values[m.group(1)] = int(m.group(2), 0)
                m2 = re.search(r'#define\s+([A-Z0-9_]+)\s+([0-9]+|0x[0-9a-fA-F]+)', line)
                if m2: action_id_values[m2.group(1)] = int(m2.group(2), 0)

    string_to_action = {}
    if os.path.exists(ACTION_TRANS_PATH):
        with open(ACTION_TRANS_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                m = re.search(r'\{\"([^\"]+)\",\s*([A-Z0-9_]+)\}', line)
                if m: string_to_action[m.group(1)] = m.group(2)

    name_to_id = {}
    id_to_names = {}
    for s_name, a_name in string_to_action.items():
        if a_name in action_id_values:
            val = action_id_values[a_name]
            name_to_id[s_name] = val
            id_to_names.setdefault(val, []).append(s_name)
    return name_to_id, id_to_names

def main():
    if len(sys.argv) < 2:
        print("用法: python kodi_id_lookup.py <button_name | button_id | action_name | action_id>")
        print("例如: python kodi_id_lookup.py return")
        print("      python kodi_id_lookup.py select")
        print("      python kodi_id_lookup.py 61453")
        sys.exit(1)

    query = sys.argv[1].lower()
    
    k_btn_name2id, k_btn_id2name = build_keyboard_button_map()
    r_btn_name2id, r_btn_id2name = build_remote_button_map()
    act_name2id, act_id2name = build_action_map()

    print(f"========== 查询结果: '{query}' ==========")
    found = False

    # 1. 尝试作为名字查找 (Button 和 Action都可以)
    if query in k_btn_name2id:
        val = k_btn_name2id[query]
        print(f"[键盘按键 <keyboard>] XML Tag名字: <{query}>  ---> ID/Code: {val} (0x{val:X})")
        aliases = [n for n in k_btn_id2name[val] if n != query]
        if aliases: print(f"   该按键ID的其他别名: {aliases}")
        found = True
        
    if query in r_btn_name2id:
        val = r_btn_name2id[query]
        print(f"[遥控按键 <remote>] XML Tag名字: <{query}>  ---> ID/Code: {val} (0x{val:X})")
        aliases = [n for n in r_btn_id2name[val] if n != query]
        if aliases: print(f"   该按键ID的其他别名: {aliases}")
        found = True

    if query in act_name2id:
        val = act_name2id[query]
        print(f"[动作 Action] 名字: \"{query}\" ---> Action ID: {val} (0x{val:X})")
        aliases = [n for n in act_id2name[val] if n != query]
        if aliases: print(f"   该动作ID的其他别名: {aliases}")
        found = True

    # 2. 尝试作为数字ID查找
    if query.isdigit() or (query.startswith('0x') and all(c in '0123456789abcdefx' for c in query)):
        num = int(query, 0)
        
        # 匹配Button ID (Keyboard)
        if num in k_btn_id2name:
            names = k_btn_id2name[num]
            print(f"[键盘按键 <keyboard>] ID/Code: {num} (0x{num:X}) ---> XML Tag名字: <{'或者'.join(names)}>")
            found = True
            
        # 匹配Button ID (Remote)
        if num in r_btn_id2name:
            names = r_btn_id2name[num]
            print(f"[遥控按键 <remote>] ID/Code: {num} (0x{num:X}) ---> XML Tag名字: <{'或者'.join(names)}>")
            found = True
            
        # 匹配Action ID
        if num in act_id2name:
            names = act_id2name[num]
            print(f"[动作 Action] ID: {num} (0x{num:X}) ---> 动作指令/XML Value: {'或者'.join(names)}")
            found = True

    if not found:
        print("未找到匹配的 Button/Key 或者 Action。")

if __name__ == '__main__':
    main()
