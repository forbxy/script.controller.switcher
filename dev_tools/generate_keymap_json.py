import os
import re
import json
import urllib.request

GITHUB_REPO = "xbmc/xbmc"
BRANCH = "Omega"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/refs/heads/{BRANCH}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_url(path):
    url = f"{BASE_URL}/{path}"
    print(f"Fetching {url}... ")
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def generate_remote_json():
    ir_header_content = fetch_url("xbmc/input/remote/IRRemote.h")
    ir_macros = {}
    for line in ir_header_content.splitlines():
        match = re.search(r'#define\s+(XINPUT_IR_REMOTE_[A-Z0-9_]+)\s+(\d+)', line)
        if match:
            ir_macros[match.group(1)] = int(match.group(2))
                
    ir_cpp_content = fetch_url("xbmc/input/keymaps/remote/IRTranslator.cpp")
    name_to_code = {}
    matches = re.finditer(r'if\s*\(\s*strButton\s*==\s*"([^"]+)"\s*\)\s+buttonCode\s*=\s*(XINPUT_IR_REMOTE_[A-Z0-9_]+)\s*;', ir_cpp_content)
    for m in matches:
        macro = m.group(2)
        if macro in ir_macros:
            name_to_code[m.group(1)] = ir_macros[macro]

    code_to_names = {}
    for name, code in name_to_code.items():
        if code not in code_to_names:
            code_to_names[code] = []
        code_to_names[code].append(name)

    result = {
        "name_to_code": name_to_code,
        "code_to_names": code_to_names
    }
    
    output_path = os.path.join(DATA_DIR, "remote_mapping.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"Generated {output_path}")

def generate_keyboard_json():
    vkeys_h_content = fetch_url("xbmc/input/keyboard/XBMC_vkeys.h")
    vkey_macros = {}
    for line in vkeys_h_content.splitlines():
        match = re.search(r'\s*(XBMCVK_[A-Z0-9_]+)\s*=\s*(0x[0-9A-Fa-f]+|\d+)', line)
        if match:
            val_str = match.group(2)
            val = int(val_str, 16) if val_str.startswith("0x") else int(val_str)
            vkey_macros[match.group(1)] = val

    keytable_cpp_content = fetch_url("xbmc/input/keyboard/XBMC_keytable.cpp")
    name_to_code = {}
    KEY_VKEY = 0xF000
    
    # The structure is `{XBMCK_BACKSPACE, 0, 0, XBMCVK_BACK, "backspace"}`
    # We need to extract the 4th element (VKEY) and 5th element (string)
    matches = re.finditer(r'\{.*?(XBMCVK_[A-Z0-9_]+)\s*,[^"]*"([^"]+)"\s*\}', keytable_cpp_content)
    for m in matches:
        vkey_name = m.group(1)
        str_name = m.group(2)
        if vkey_name in vkey_macros:
            code_val = vkey_macros[vkey_name]
            final_code = code_val | KEY_VKEY
            name_to_code[str_name] = final_code

    # Add single characters explicitly mapped to UNICODE space in Kodi if defined, but string map is usually enough here
    code_to_names = {}
    for name, code in name_to_code.items():
        if code not in code_to_names:
            code_to_names[code] = []
        code_to_names[code].append(name)

    result = {
        "name_to_code": name_to_code,
        "code_to_names": code_to_names
    }
    
    output_path = os.path.join(DATA_DIR, "keyboard_mapping.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_remote_json()
    generate_keyboard_json()
