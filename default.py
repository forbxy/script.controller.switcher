# -*- coding: utf-8 -*-
import os
import shutil
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

def get_icon_path():
    return os.path.join(ADDON_PATH, "icon.png")

def notification(message, title="RemoteSwitcher", duration=1000, sound=False):
    xbmcgui.Dialog().notification(title, message, get_icon_path(), duration, sound)

def log(msg, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_ID}] {msg}", level)

def get_keymaps_dir():
    # Kodi keymaps path
    keymaps_dir = xbmcvfs.translatePath('special://userdata/keymaps/')

    if not os.path.exists(keymaps_dir):
        try:
            os.makedirs(keymaps_dir)
        except OSError:
            pass

    return keymaps_dir

def get_hwdb_dir():
    # 智能识别 hwdb.d 目录
    possible_paths = [
        '/storage/.config/hwdb.d',   # CoreELEC / LibreELEC
        '/etc/udev/hwdb.d',          # Standard Linux
        '/lib/udev/hwdb.d',          # Alternative Linux
    ]
    for p in possible_paths:
        if os.path.exists(p) and os.path.isdir(p):
            return p
            
    return ''

def get_evdev_line(filepath):
    """Retrieve the evdev match line from the hwdb file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('evdev:'):
                return line
    return None

def get_unique_backup_path(filepath):
    """Generate a unique backup path without overwriting existing ones."""
    bak_path = filepath + '.bak'
    counter = 1
    while os.path.exists(bak_path):
        bak_path = filepath + f'.bak{counter}'
        counter += 1
    return bak_path

def load_remotes(remotes_txt):
    if not os.path.exists(remotes_txt):
        notification('找不到 remotes.txt', title='错误')
        return []

    remotes = []
    # 获取当前运行的系统平台，转换成小写
    system_hw = xbmc.getCondVisibility('System.Platform.Linux') and 'linux' or \
                xbmc.getCondVisibility('System.Platform.Android') and 'android' or \
                xbmc.getCondVisibility('System.Platform.Windows') and 'windows' or 'unknown'
                
    with open(remotes_txt, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            parts = line.split(':')
            name = parts[0]
            path = parts[1] if len(parts) > 1 else ""
            platforms = parts[2] if len(parts) > 2 else ""
            
            # 如果配置了平台，并且当前平台不在配置的列表中，则跳过
            if platforms and system_hw != 'unknown':
                if system_hw not in platforms.split('_'):
                    continue
                    
            remotes.append({'name': name, 'path': path})
    
    if not remotes:
        notification('没有找到任何遥控器配置', title='错误')
    return remotes

def select_remote(remotes):
    if not remotes:
        return None

    keymaps_dir = get_keymaps_dir()

    processed_remotes = []
    for r in remotes:
        dir_name = os.path.basename(os.path.normpath(r['path']))

        is_in_use = False
        possible_files = [
            f"a-{dir_name}.xml",
            f"a-{dir_name}-merged.xml",
            f"z-{dir_name}-overwrite.xml",
        ]

        if os.path.exists(keymaps_dir):
            for file in possible_files:
                if os.path.exists(os.path.join(keymaps_dir, file)):
                    is_in_use = True
                    break

        display_name = r['name']
        if is_in_use:
            display_name += " [COLOR yellow]←[当前部署设备][/COLOR]"

        processed_remotes.append((is_in_use, r, display_name))

    # 稳定排序: 正在使用的排在最前面
    processed_remotes.sort(key=lambda x: x[0], reverse=True)
    
    sorted_remotes = [item[1] for item in processed_remotes]
    names = [item[2] for item in processed_remotes]

    index = xbmcgui.Dialog().select('选择控制器', names)
    if index < 0:
        return None, False
    is_in_use = processed_remotes[index][0] if index < len(processed_remotes) else False
    return sorted_remotes[index], is_in_use

def merge_xml_files(base_path, overwrite_path, output_path):
    import xml.etree.ElementTree as ET
    try:
        base_tree = ET.parse(base_path)
        base_root = base_tree.getroot()
        
        over_tree = ET.parse(overwrite_path)
        over_root = over_tree.getroot()
        
        for over_window in over_root:
            base_window = base_root.find(over_window.tag)
            if base_window is None:
                base_root.append(over_window)
                continue
                
            for over_device in over_window:
                base_device = base_window.find(over_device.tag)
                if base_device is None:
                    base_window.append(over_device)
                    continue
                    
                for over_key in over_device:
                    key_id = over_key.get('id')
                    key_mod = over_key.get('mod')
                    
                    existing_key = None
                    for k in base_device:
                        if k.tag == over_key.tag and k.get('id') == key_id and k.get('mod') == key_mod:
                            existing_key = k
                            break
                            
                    if existing_key is not None:
                        base_device.remove(existing_key)
                    base_device.append(over_key)
                    
        base_tree.write(output_path, encoding='utf-8', xml_declaration=True)
        return True
    except Exception as e:
        log(f"合并XML失败: {e}", xbmc.LOGERROR)
        return False

def get_remote_files(selected_path):
    dir_name = os.path.basename(os.path.normpath(selected_path))
    
    addon_source_dir = os.path.join(ADDON_PATH, os.path.normpath(selected_path))
    
    src_hwdb = None
    if os.path.exists(addon_source_dir):
        for file in os.listdir(addon_source_dir):
            if file.endswith('.hwdb'):
                src_hwdb = os.path.join(addon_source_dir, file)
                break
                
    exact_xml = os.path.join(addon_source_dir, f"a-{dir_name}.xml")
    overwrite_xml = os.path.join(addon_source_dir, f"a-{dir_name}-overwrite.xml")
    general_xml = os.path.join(ADDON_PATH, 'data', 'general.xml')

    src_xml = None
    target_xml_name = None
    
    if os.path.exists(exact_xml):
        src_xml = exact_xml
        target_xml_name = f"a-{dir_name}.xml"
    elif os.path.exists(overwrite_xml) and os.path.exists(general_xml):
        tmp_dir = xbmcvfs.translatePath('special://temp')
        tmp_xml = os.path.join(tmp_dir, f"a-{dir_name}-merged.xml")
        if merge_xml_files(general_xml, overwrite_xml, tmp_xml):
            src_xml = tmp_xml
            target_xml_name = f"a-{dir_name}-merged.xml"
    else:
        # 如果以上都没有，直接查找通用配置并沿用
        if os.path.exists(general_xml):
            src_xml = general_xml
            target_xml_name = f"a-{dir_name}.xml"

    return src_hwdb, src_xml, target_xml_name

def deploy_hwdb(src_hwdb, hwdb_dir):
    if not src_hwdb:
        return True
        
    target_evdev = get_evdev_line(src_hwdb)
    new_hwdb_name = os.path.basename(src_hwdb)
    if not hwdb_dir:
        notification('未找到 hwdb 目录，无法更新 hwdb 文件', title='错误', sound=True)
        return False
        
    try:
        if os.path.exists(hwdb_dir):
            for file in os.listdir(hwdb_dir):
                if not file.endswith('.hwdb'):
                    continue
                
                filepath = os.path.join(hwdb_dir, file)
                if file == new_hwdb_name:
                    continue
                    
                if target_evdev:
                    evdev = get_evdev_line(filepath)
                    if evdev == target_evdev:
                        bak_path = get_unique_backup_path(filepath)
                        shutil.move(filepath, bak_path)
                        
        target_path = os.path.join(hwdb_dir, new_hwdb_name)
        
        with open(src_hwdb, 'r', encoding='utf-8') as f:
            src_content = f.read()
            
        if os.path.exists(target_path):
            try:
                import hashlib
                import re
                with open(target_path, 'r', encoding='utf-8') as f:
                    target_content = f.read()
                    
                # 统一抹去源文件和目标文件中的 "{TIME}" 占位符以及可能已经被写入的真实时间戳
                pattern = r'(\{TIME\}|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                src_normalized = re.sub(pattern, '', src_content)
                target_normalized = re.sub(pattern, '', target_content)
                
                src_hash = hashlib.md5(src_normalized.encode('utf-8')).hexdigest()
                target_hash = hashlib.md5(target_normalized.encode('utf-8')).hexdigest()
                
                if src_hash == target_hash:
                    log("目标 hwdb 文件已存在且内容一致，跳过写入", level=xbmc.LOGINFO)
                    return True
            except Exception as e:
                log(f"校验旧 hwdb 文件失败: {e}", level=xbmc.LOGINFO)

        # Process the hwdb file to inject current time before copying
        import datetime
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        content = src_content.replace('{TIME}', current_time)
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return True
    except Exception as e:
        log(f"操作 hwdb 文件失败 (可能无权限): {e}", xbmc.LOGERROR, sound=True)
        try:
            # Fallback copy if failure was due to processing
            shutil.copy2(src_hwdb, target_path)
            return True
        except Exception:
            xbmcgui.Dialog().ok(
                "权限不足",
                f"无法写入 hwdb 目录，请手动将文件:\n[COLOR yellow]{src_hwdb}[/COLOR]\n\n"
                f"拷贝至:\n[COLOR yellow]{hwdb_dir}[/COLOR]\n\n"
                "然后通过 SSH 执行 systemd-hwdb update 及 udevadm trigger。"
            )
            return False

def deploy_xml(src_xml, keymaps_dir, target_xml_name=None):
    if not target_xml_name:
        target_xml_name = os.path.basename(src_xml) if src_xml else None
    
    new_xml_name = target_xml_name
    
    # Extract the base remote dir name from target_xml_name to reuse backup logic
    # Example: target_xml_name could be 'a-g20spro.xml' or 'a-g20spro-merged.xml'
    # We strip 'a-' at the beginning and '.xml' at the end to pass to backup_remove_other_remotes_xmls
    current_dir_name = new_xml_name
    if current_dir_name:
        if current_dir_name.startswith('a-'):
            current_dir_name = current_dir_name[2:]
        if current_dir_name.endswith('.xml'):
            current_dir_name = current_dir_name[:-4]
        if current_dir_name.endswith('-merged'):
            current_dir_name = current_dir_name[:-7]
            
        backup_remove_other_remotes_xmls(keymaps_dir, current_dir_name)

    if src_xml:
        target_path = os.path.join(keymaps_dir, new_xml_name)
        try:
            with open(src_xml, 'r', encoding='utf-8') as f:
                content = f.read()

            import datetime
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            content = content.replace('{TIME}', current_time)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            log(f"复制并处理 xml 文件失败: {e}", xbmc.LOGERROR, sound=True)
            shutil.copy2(src_xml, target_path)

def deploy_linux(src_hwdb, src_xml, target_xml_name, remote_name):
    hwdb_dir = get_hwdb_dir()
    keymaps_dir = get_keymaps_dir()
    
    hwdb_success = deploy_hwdb(src_hwdb, hwdb_dir)
    deploy_xml(src_xml, keymaps_dir, target_xml_name)
    
    if hwdb_success:
        try:
            os.system('systemd-hwdb update')
            os.system('udevadm trigger')
        except Exception as e:
            log(f"刷新 hwdb 失败: {e}", xbmc.LOGERROR, sound=True)

        xbmc.executebuiltin('Action(ReloadKeymaps)')
        notification(f"已成功部署 {remote_name} 默认配置并加载 (Linux)", title='成功')
    else:
        xbmc.executebuiltin('Action(ReloadKeymaps)')
        notification(f"按键映射已更新，但 hwdb 需手动处理", title='部分成功')

def deploy_android(src_xml, target_xml_name, remote_name):
    keymaps_dir = get_keymaps_dir()
    deploy_xml(src_xml, keymaps_dir, target_xml_name)
    xbmc.executebuiltin('Action(ReloadKeymaps)')
    notification(f"已成功部署 {remote_name} 默认配置并加载 (Android)", title='成功')

def deploy_windows(src_xml, target_xml_name, remote_name):
    keymaps_dir = get_keymaps_dir()
    deploy_xml(src_xml, keymaps_dir, target_xml_name)
    xbmc.executebuiltin('Action(ReloadKeymaps)')
    notification(f"已成功部署 {remote_name} 默认配置并加载 (Windows)", title='成功')

def clear_deployed_files(selected_path, remote_name):
    src_hwdb, src_xml, target_xml_name = get_remote_files(selected_path)
    cleared = 0

    # 清除该遥控器对应的 xml 文件
    keymaps_dir = get_keymaps_dir()
    dir_name = os.path.basename(os.path.normpath(selected_path))
    
    # 不移除属于用户自定义的 z-xxx-overwrite.xml 配置
    possible_xmls = [
        f"a-{dir_name}.xml",
        f"a-{dir_name}-merged.xml",
    ]
    
    for px in possible_xmls:
        px_path = os.path.join(keymaps_dir, px)
        if os.path.exists(px_path):
            os.remove(px_path)
            cleared += 1

    # Linux 下清除该遥控器对应的 hwdb 文件
    if xbmc.getCondVisibility('System.Platform.Linux') and src_hwdb:
        hwdb_dir = get_hwdb_dir()
        if hwdb_dir:
            hwdb_name = os.path.basename(src_hwdb)
            target_hwdb_path = os.path.join(hwdb_dir, hwdb_name)
            if os.path.exists(target_hwdb_path):
                try:
                    os.remove(target_hwdb_path)
                    cleared += 1
                except Exception as e:
                    log(f"清空 hwdb 文件失败 (可能无权限): {e}", xbmc.LOGERROR, sound=True)

            try:
                os.system('systemd-hwdb update')
                os.system('udevadm trigger')
            except Exception as e:
                log(f"刷新 hwdb 失败: {e}", xbmc.LOGERROR, sound=True)

    xbmc.executebuiltin('Action(ReloadKeymaps)')
    if cleared:
        notification(f"已清空 {remote_name} 的 {cleared} 个适配文件", title='成功')
    else:
        notification(f"{remote_name} 没有已部署的适配文件", title='提示')

def backup_remove_other_remotes_xmls(keymaps_dir, current_dir_name):
    """备份并移除不属于当前所选遥控器的 xml 文件"""
    if not os.path.exists(keymaps_dir):
        return
        
    allowed_names = [
        f"a-{current_dir_name}.xml",
        f"a-{current_dir_name}-merged.xml",
        f"z-{current_dir_name}-overwrite.xml",
    ]
    
    cleared = False
    for file in os.listdir(keymaps_dir):
        if not file.endswith('.xml'):
            continue
            
        if file in allowed_names:
            continue
            
        filepath = os.path.join(keymaps_dir, file)
        
        # 本插件创建的配置文件使用 .saved 备份，以便切换回来时还原
        if file.startswith('a-') or (file.startswith('z-') and file.endswith('-overwrite.xml')):
            saved_path = filepath + '.saved'
            if os.path.exists(saved_path):
                os.remove(saved_path)
            shutil.move(filepath, saved_path)
            log(f"Saved for later restore: {file} -> {file}.saved")
        else:
            # 非本插件创建的第三方 xml 使用 .bak 备份
            bak_path = get_unique_backup_path(filepath)
            shutil.move(filepath, bak_path)
            log(f"Backed up third-party xml: {file} -> {os.path.basename(bak_path)}")
        
        cleared = True
        
    if cleared:
        xbmc.executebuiltin('Action(ReloadKeymaps)')

def get_saved_files(keymaps_dir, dir_name):
    """检查该遥控器是否有 .saved 备份文件，返回列表"""
    saved = []
    candidates = [
        f"a-{dir_name}.xml.saved",
        f"a-{dir_name}-merged.xml.saved",
        f"z-{dir_name}-overwrite.xml.saved",
    ]
    for name in candidates:
        if os.path.exists(os.path.join(keymaps_dir, name)):
            saved.append(name)
    return saved

def restore_saved_files(keymaps_dir, dir_name):
    """还原该遥控器之前保存的所有配置文件"""
    candidates = [
        f"a-{dir_name}.xml",
        f"a-{dir_name}-merged.xml",
        f"z-{dir_name}-overwrite.xml",
    ]
    restored = []
    for name in candidates:
        target_path = os.path.join(keymaps_dir, name)
        saved_path = target_path + '.saved'
        if os.path.exists(saved_path):
            # 如果当前已存在同名文件，先移除
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.move(saved_path, target_path)
            restored.append(name)
            log(f"Restored saved config: {name}")
    return restored

def show_text_file(filepath, title):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            xbmcgui.Dialog().textviewer(title, text)
        except Exception as e:
            log(f"读取说明失败: {e}", xbmc.LOGERROR, sound=True)
    else:
        notification('暂未提供此说明文件', title='提示')

def switch_to_remote(selected_path, remote_name):
    """切换到指定遥控器：备份其他遥控器配置，还原或创建当前遥控器配置"""
    keymaps_dir = get_keymaps_dir()
    dir_name = os.path.basename(os.path.normpath(selected_path))
    
    # 先备份其他遥控器的配置
    backup_remove_other_remotes_xmls(keymaps_dir, dir_name)
    
    # 尝试还原之前保存的配置
    saved_files = get_saved_files(keymaps_dir, dir_name)
    if saved_files:
        restored = restore_saved_files(keymaps_dir, dir_name)
        if restored:
            xbmc.executebuiltin('Action(ReloadKeymaps)')
            notification(f"已切换到 {remote_name} 并还原之前的配置", title='成功')
            return
    
    # 没有备份，创建用户自定义按键的占位 xml 并部署 hwdb
    src_hwdb, src_xml, target_xml_name = get_remote_files(selected_path)
    
    overwrite_xml_name = f"z-{dir_name}-overwrite.xml"
    overwrite_path = os.path.join(keymaps_dir, overwrite_xml_name)
    if not os.path.exists(overwrite_path):
        with open(overwrite_path, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="utf-8"?>\n<keymap>\n</keymap>\n')
    
    # Linux 下同时部署 hwdb
    if xbmc.getCondVisibility('System.Platform.Linux') and src_hwdb:
        hwdb_dir = get_hwdb_dir()
        if deploy_hwdb(src_hwdb, hwdb_dir):
            try:
                os.system('systemd-hwdb update')
                os.system('udevadm trigger')
            except Exception as e:
                log(f"刷新 hwdb 失败: {e}", xbmc.LOGERROR, sound=True)
    
    xbmc.executebuiltin('Action(ReloadKeymaps)')
    notification(f"已切换到 {remote_name}", title='成功')

def main():
    remotes_txt = os.path.join(ADDON_PATH, 'remotes.txt')
    remotes = load_remotes(remotes_txt)
    
    while True:
        selected, is_in_use = select_remote(remotes)
        if not selected:
            break

        source_dir = os.path.join(ADDON_PATH, os.path.normpath(selected['path']))
        if not os.path.exists(source_dir):
            notification(f"找不到目录: {selected['path']}", title='错误')
            log(f"找不到目录: {selected['path']}", xbmc.LOGERROR, sound=True)
            continue

        if not is_in_use:
            # 非当前遥控器：显示切换选项和说明
            options = ["切换到该控制器"]
            actions = ["switch"]
            
            connect_file = os.path.join(source_dir, 'connect.txt')
            if os.path.exists(connect_file):
                options.append("连接说明书")
                actions.append("connect")
            desc_file = os.path.join(source_dir, 'desc.txt')
            if os.path.exists(desc_file):
                options.append("适配说明书")
                actions.append("desc")
            
            menu_index = xbmcgui.Dialog().select(f"{selected['name']}", options)
            if menu_index == -1:
                continue
            
            action = actions[menu_index]
            if action == "switch":
                switch_to_remote(selected['path'], selected['name'])
                is_in_use = True
                # 切换成功后直接进入当前遥控器的完整操作菜单（下方）
            elif action == "connect":
                show_text_file(connect_file, f"{selected['name']} 连接与红外学习说明")
                continue
            elif action == "desc":
                show_text_file(desc_file, f"{selected['name']} 遥控器映射说明")
                continue
            else:
                continue
        
        if not is_in_use:
            continue
            continue

        # 当前遥控器：显示完整操作菜单
        while True:
            src_hwdb, src_xml, target_xml_name = get_remote_files(selected['path'])
            
            # 检查默认配置文件是否已加载
            keymaps_dir = get_keymaps_dir()
            dir_name = os.path.basename(os.path.normpath(selected['path']))
            has_default_loaded = os.path.exists(os.path.join(keymaps_dir, f"a-{dir_name}.xml")) or \
                                 os.path.exists(os.path.join(keymaps_dir, f"a-{dir_name}-merged.xml"))
            
            options = []
            actions = []
            connect_file = os.path.join(source_dir, 'connect.txt')
            if os.path.exists(connect_file):
                options.append("连接说明书")
                actions.append("connect")

            options.append("加载默认适配文件")
            actions.append("replace")
            if has_default_loaded:
                options.append("移除默认适配文件")
                actions.append("clear")
            desc_file = os.path.join(source_dir, 'desc.txt')
            if os.path.exists(desc_file):
                options.append("默认适配说明书")
                actions.append("desc")
            
            if has_default_loaded:
                options.append("编辑已加载的默认配置文件")
                actions.append("edit_default")
            
            if xbmc.getCondVisibility('System.Platform.Linux') and src_hwdb:
                options.append("加载默认适配文件(仅hwdb文件)")
                actions.append("replace_hwdb_only")
                hwdb_dir = get_hwdb_dir()
                if hwdb_dir:
                    hwdb_name = os.path.basename(src_hwdb)
                    if os.path.exists(os.path.join(hwdb_dir, hwdb_name)):
                        options.append("移除默认适配文件(仅hwdb文件)")
                        actions.append("clear_hwdb_only")
            
            options.append("编辑自定义适配文件")
            actions.append("custom")

            menu_index = xbmcgui.Dialog().select(f"操作选项 - {selected['name']}", options)
            
            if menu_index == -1:
                break
            
            action = actions[menu_index]

            if action == "replace":
                if not src_hwdb and not src_xml:
                    notification('所选遥控器缺少配置(hwdb或xml)文件', title='错误')
                    log(f"所选遥控器缺少配置(hwdb或xml)文件: {selected['path']}", xbmc.LOGERROR, sound=True)
                    continue

                if xbmc.getCondVisibility('System.Platform.Linux'):
                    deploy_linux(src_hwdb, src_xml, target_xml_name, selected['name'])
                elif xbmc.getCondVisibility('System.Platform.Android'):
                    deploy_android(src_xml, target_xml_name, selected['name'])
                elif xbmc.getCondVisibility('System.Platform.Windows'):
                    deploy_windows(src_xml, target_xml_name, selected['name'])
                else:
                    notification("未知系统平台，尝试通用部署", title="警告")
                    deploy_android(src_xml, target_xml_name, selected['name'])

            elif action == "replace_hwdb_only":
                hwdb_dir = get_hwdb_dir()
                hwdb_success = deploy_hwdb(src_hwdb, hwdb_dir)
                if hwdb_success:
                    try:
                        os.system('systemd-hwdb update')
                        os.system('udevadm trigger')
                    except Exception as e:
                        log(f"刷新 hwdb 失败: {e}", xbmc.LOGERROR, sound=True)
                    notification(f"仅加载了 hwdb 并刷新配置 (Linux)", title='成功')
                else:
                    notification(f"hwdb 需手动处理", title='失败')
                    
            elif action == "clear_hwdb_only":
                if xbmcgui.Dialog().yesno('确认移除', f"确定要移除 {selected['name']} 的 hwdb 文件吗？"):
                    hwdb_dir = get_hwdb_dir()
                    cleared = 0
                    if hwdb_dir:
                        hwdb_name = os.path.basename(src_hwdb)
                        target_hwdb_path = os.path.join(hwdb_dir, hwdb_name)
                        if os.path.exists(target_hwdb_path):
                            try:
                                os.remove(target_hwdb_path)
                                cleared += 1
                                try:
                                    os.system('systemd-hwdb update')
                                    os.system('udevadm trigger')
                                except Exception as e:
                                    log(f"刷新 hwdb 失败: {e}", xbmc.LOGERROR, sound=True)
                            except Exception as e:
                                log(f"清空 hwdb 文件失败 (可能无权限): {e}", xbmc.LOGERROR, sound=True)

                    if cleared:
                        notification(f"已清空 hwdb 文件", title='成功')
                    else:
                        notification(f"没有找到已部署的 hwdb 文件", title='提示')
                
            elif action == "clear":
                if xbmcgui.Dialog().yesno('确认移除', f"确定要移除 {selected['name']} 的适配文件吗？"):
                    clear_deployed_files(selected['path'], selected['name'])

            elif action == "connect":
                show_text_file(connect_file, f"{selected['name']} 连接与红外学习说明")
                
            elif action == "desc":
                show_text_file(desc_file, f"{selected['name']} 遥控器映射说明")
                
            elif action == "edit_default":
                from custom_keymap import manage_custom_keymap
                keymaps_dir = get_keymaps_dir()
                dir_name = os.path.basename(os.path.normpath(selected['path']))
                
                backup_remove_other_remotes_xmls(keymaps_dir, dir_name)
                
                merged_path = os.path.join(keymaps_dir, f"a-{dir_name}-merged.xml")
                exact_path = os.path.join(keymaps_dir, f"a-{dir_name}.xml")
                
                target_xml_path = None
                if os.path.exists(merged_path):
                    target_xml_path = merged_path
                elif os.path.exists(exact_path):
                    target_xml_path = exact_path
                else: 
                    target_xml_path = os.path.join(keymaps_dir, target_xml_name) if target_xml_name else None
                
                if not target_xml_path or not os.path.exists(target_xml_path):
                    xbmcgui.Dialog().ok("提示", "您尚未加载该设备的默认配置文件。\n请先执行 [加载默认适配文件]。")
                else:
                    manage_custom_keymap(target_xml_path, f"{selected['name']} (默认配置)")
                
            elif action == "custom":
                from custom_keymap import manage_custom_keymap
                keymaps_dir = get_keymaps_dir()
                dir_name = os.path.basename(os.path.normpath(selected['path']))
                
                backup_remove_other_remotes_xmls(keymaps_dir, dir_name)
                
                overwrite_xml_path = os.path.join(keymaps_dir, f"z-{dir_name}-overwrite.xml")
                
                manage_custom_keymap(overwrite_xml_path, selected['name'])

if __name__ == '__main__':
    main()
    
