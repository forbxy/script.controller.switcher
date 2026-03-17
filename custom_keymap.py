# -*- coding: utf-8 -*-
import os
import shutil
import xml.etree.ElementTree as ET
from threading import Timer
from collections import OrderedDict
import json

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

ACTIONS = OrderedDict([
    ("常用", OrderedDict([
        ("playerprocessinfo", "播放器进程信息"),
        ("activatewindow(settings)", "设置"),
        ("playpause", "播放/暂停"),
        ("skipnext", "播放下一个"),
        ("skipprevious", "播放上一个"),
        ("stop", "停止播放"),
        ("fastforward", "快进"),
        ("rewind", "快退"),
        ("activatewindow(playercontrols)", "打开播放控制器"),
        ("fullscreen", "在菜单与全屏播放界面间切换"),
        ("screenshot", "截屏"),
        ("info", "显示信息"),
        ("contextmenu", "上下文菜单"),
        ("audiodelayminus", "音频延迟减少"),
        ("audiodelayplus", "音频延迟增加"),
        ("subtitledelayminus", "字幕延迟减少"),
        ("subtitledelayplus", "字幕延迟增加"),
        ("updatelibrary(video)", "更新视频库"),
        ("activatewindow(shutdownmenu)", "关机菜单"),
        ("activatewindow(programs)", "打开插件/程序页面"),
    ])),
    ("Forbxy插件", OrderedDict([
        ("runscript(plugin.video.filteredmovies, 0, ?mode=launch_t9)", "加载筛选页面"),
        ("runscript(plugin.video.filteredmovies, ?mode=select_subtitle)", "加载字幕选择页面"),
        ("runscript(plugin.video.filteredmovies, ?mode=select_audio)", "加载音轨选择页面"),
        ("runscript(plugin.video.filteredmovies, ?mode=record_skip_point)", "标记片头/片尾时间点"),
        ("runscript(plugin.video.filteredmovies, ?mode=delete_skip_point)", "删除片头/片尾时间点标记"),
        ("runscript(plugin.video.filteredmovies, ?mode=open_playing_tvshow)", "打开当前播放电视剧的剧集列表"),
        ("runscript(plugin.video.filteredmovies, ?mode=force_prev)", "强制播放上一个"),
        ("runscript(plugin.video.filteredmovies, ?mode=toggle_favourite)", "将项目添加到收藏夹或从收藏夹移除"),
        ("runscript(plugin.cloudstorage.webdav.refresh)", "刷新WebDAV/OpenList目录"),
        ("runscript(plugin.cloudstorage.webdav.refresh, recursive=true)", "递归刷新WebDAV/OpenList目录"),
    ])),
    ("界面导航", OrderedDict([
        ("left", "向左移动"),
        ("right", "向右移动"),
        ("up", "向上移动"),
        ("down", "向下移动"),
        ("pageup", "上一页"),
        ("pagedown", "下一页"),
        ("select", "确认/进入"),
        ("highlight", "勾选/标记文件(多选操作时)"),
        ("parentfolder", "返回上级目录"),
        ("back", "返回"),
        ("previousmenu", "返回上一级菜单"),
        ("info", "显示项目信息"),
        ("contextmenu", "呼出选项菜单(上下文/右键菜单)"),
        ("menu", "打开侧边栏菜单"),
        ("firstpage", "跳转至列表首项"),
        ("lastpage", "跳转至列表末项"),
        ("nextletter", "在列表中跳转至下一首字母"),
        ("prevletter", "在列表中跳转至上一首字母"),
        ("scrollup", "向上平滑滚动"),
        ("scrolldown", "向下平滑滚动"),
        ("cursorleft", "输入框光标左移"),
        ("cursorright", "输入框光标右移"),
    ])),
    ("播放相关", OrderedDict([
        ("play", "播放"),
        ("pause", "暂停"),
        ("playpause", "播放/暂停"),
        ("stop", "停止播放"),
        ("skipnext", "播放下一个"),
        ("skipprevious", "播放上一个"),
        ("fastforward", "快进"),
        ("rewind", "快退"),
        ("smallstepback", "小幅步退"),
        ("stepforward", "步进"),
        ("stepback", "步退"),
        ("bigstepforward", "大幅步进"),
        ("bigstepback", "大幅步退"),
        ("osd", "显示播放菜单"),
        ("showtime", "显示时间"),
        ("playlist", "显示播放列表"),
        ("fullscreen", "在菜单与全屏播放界面间切换"),
        ("aspectratio", "循环切换画面显示比例(宽高比)"),
        ("showvideomenu", "显示DVD/蓝光菜单"),
        ("createbookmark", "创建书签"),
        ("createepisodebookmark", "创建剧集书签"),
        ("togglestereomode", "切换3D模式(Stereo)"),
        ("switchplayer", "切换播放器"),
        ("playnext", "设定为下一个播放/插队"),
        ("playerprogramselect", "选择节目流(TS多路复用)"),
        ("playerresolutionselect", "选择屏幕分辨率(需先配置白名单)"),
        ("verticalshiftup", "视频画面垂直向上移动(并切换为自定义视图)"),
        ("verticalshiftdown", "视频画面垂直向下移动(并切换为自定义视图)"),
        ("playercontrol(tempoup)", "播放速度+"),
        ("playercontrol(tempodown)", "播放速度-"),
        ("nextscene", "下一场景(需edl场景标记文件)"),
        ("previousscene", "上一场景(需edl场景标记文件)"),
        ("chapterorbigstepforward", "下一章节/无章节时大幅步进"),
        ("chapterorbigstepback", "上一章节/无章节时大幅步退"),
        ("videonextstream", "下一视频流"),
        ("hdrtoggle", "强制开关屏幕HDR状态"),
        ("stereomode", "打开3D模式(Stereo)选择面板"),
        ("nextstereomode", "下一3D模式(Stereo)"),
        ("previousstereomode", "上一3D模式(Stereo)"),
        ("stereomodetomono", "3D转2D单画面"),
    ])),
    ("音频相关", OrderedDict([
        ("mute", "静音"),
        ("volumeup", "设备音量+"),
        ("volumedown", "设备音量-"),
        ("audionextlanguage", "切换音轨语言"),
        ("audiodelay", "打开音频同步/延迟调节面板"),
        ("audiodelayminus", "音频延迟减少"),
        ("audiodelayplus", "音频延迟增加"),
        ("audiotoggledigital", "开启/关闭音频直通"),
        ("volampup", "音量软件增益+(dB)"),
        ("volampdown", "音量软件增益-(dB)"),
        ("volumeamplification", "打开音量软件增益调节面板"),
    ])),
    ("图片相关", OrderedDict([
        ("nextpicture", "下一张图片"),
        ("previouspicture", "上一张图片"),
        ("rotate", "顺时针旋转"),
        ("rotateccw", "逆时针旋转"),
        ("zoomout", "缩小"),
        ("zoomin", "放大"),
        ("zoomnormal", "回到正常缩放"),
        ("zoomlevel1", "切换到缩放级别 1"),
        ("zoomlevel2", "切换到缩放级别 2"),
        ("zoomlevel3", "切换到缩放级别 3"),
        ("zoomlevel4", "切换到缩放级别 4"),
        ("zoomlevel5", "切换到缩放级别 5"),
        ("zoomlevel6", "切换到缩放级别 6"),
        ("zoomlevel7", "切换到缩放级别 7"),
        ("zoomlevel8", "切换到缩放级别 8"),
        ("zoomlevel9", "切换到缩放级别 9"),
    ])),
    ("字幕相关", OrderedDict([
        ("showsubtitles", "显示/隐藏字幕"),
        ("nextsubtitle", "下一字幕"),
        ("browsesubtitle", "浏览并手动外挂字幕"),
        ("cyclesubtitle", "循环切换字幕"),
        ("subtitledelay", "打开字幕同步/延迟调节面板"),
        ("subtitledelayminus", "字幕延迟减少"),
        ("subtitledelayplus", "字幕延迟增加"),
        ("subtitlealign", "循环切换字幕位置(底部/顶部/画面内等)"),
        ("subtitleshiftup", "字幕向上移动"),
        ("subtitleshiftdown", "字幕向下移动"),
    ])),
    ("电视及广播/PVR", OrderedDict([
        ("channelup", "上一频道"),
        ("channeldown", "下一频道"),
        ("previouschannelgroup", "上一频道组"),
        ("nextchannelgroup", "下一频道组"),
        ("playpvr", "播放最新的 PVR"),
        ("playpvrtv", "播放本地电视(PVR)"),
        ("playpvrradio", "播放广播电台(PVR)"),
        ("record", "录制当前节目/设置定时录制"),
        ("togglecommskip", "开启/关闭自动跳过广播广告"),
        ("showtimerrule", "打开定时录制规则面板"),
        ("channelnumberseparator", "数字键: 频道分隔符(如12.1)"),
    ])),
    ("对当前选中项目(音乐,电影或文件等)的操作", OrderedDict([
        ("queue", "添加到当前播放队列"),
        ("delete", "删除文件或从媒体库中移除"),
        ("copy", "复制项目(主要用于文件管理器)"),
        ("move", "移动项目(主要用于文件管理器)"),
        ("moveitemup", "在播放队列中将项目上移"),
        ("moveitemdown", "在播放队列中将项目下移"),
        ("rename", "重命名文件或文件夹"),
        ("scanitem", "单独扫描/刮削该项目到媒体库"),
        ("togglewatched", "切换观看状态(已观看/未观看)"),
        ("increaserating", "提高评分(仅限正在播放的音乐)"),
        ("decreaserating", "降低评分(仅限正在播放的音乐)"),
        ("setrating", "打开评分面板(仅限正在播放的音乐)"),
    ])),
    ("系统相关", OrderedDict([
        ("togglefullscreen", "切换Kodi为全屏或窗口化模式"),
        ("minimize", "最小化"),
        ("shutdown", "关机"),
        ("reboot", "重启"),
        ("hibernate", "休眠"),
        ("suspend", "睡眠/挂起"),
        ("restartapp", "重启Kodi"),
        ("system.logoff", "注销当前配置"),
        ("quit", "退出Kodi"),
        ("settingsreset", "将当前页的设置重置为默认值"),
        ("settingslevelchange", "更改设置可见级别"),
        ("togglefont", "切换字体"),
        ("reloadskin", "重新加载皮肤"),
    ])),
    ("虚拟键盘", OrderedDict([
        ("enter", "提交/完成输入"),
        ("shift", "切换大小写"),
        ("symbols", "切换符号面板"),
        ("backspace", "退格删除"),
        ("number0", "数字 0 "),
        ("number1", "数字 1 "),
        ("number2", "数字 2 "),
        ("number3", "数字 3 "),
        ("number4", "数字 4 "),
        ("number5", "数字 5 "),
        ("number6", "数字 6 "),
        ("number7", "数字 7 "),
        ("number8", "数字 8 "),
        ("number9", "数字 9 "),
        ("red", "红键(通常为退格)"),
        ("green", "绿键(通常为完成)"),
        ("yellow", "黄键(通常为Shift)"),
        ("blue", "蓝键(通常为符号)"),
    ])),
    ("取消与禁用", OrderedDict([
        ("", "擦除预设映射 (穿透到系统)"),
        ("noop", "彻底禁用按键 (无任何反应)"),
    ])),
    ("其他", OrderedDict([
        ("updatelibrary(video)", "更新视频库"),
        ("updatelibrary(music)", "更新音乐库"),
        ("cleanlibrary(video)", "清理视频库(移除文件已不存在的库记录)"),
        ("cleanlibrary(music)", "清理音乐库(移除文件已不存在的库记录)"),
        ("playerprocessinfo", "显示播放器进程信息分析页(音视频解码格式,码率等)"),
        ("playerdebug", "显示内核播放器调试信息(A-V音画同步,队列及丢帧)"),
        ("playerdebugvideo", "显示底层视频渲染器调试信息(OpenGL/DX色彩与送显)"),
        ("screenshot", "截屏"),
        ("reloadkeymaps", "重新加载自定义按键"),
        ("increasepar", "拉长画面像素(增加PAR比例)"),
        ("decreasepar", "压扁画面像素(减少PAR比例)"),
        ("nextresolution", "[屏显设置专属] 下一分辨率"),
        ("nextcalibration", "[屏显设置专属] 下一校准步骤"),
        ("resetcalibration", "[屏显设置专属] 重置校准参数"),
        ("showpreset", "音乐可视化效果->显示预设"),
        ("presetlist", "音乐可视化效果->预设列表"),
        ("nextpreset", "音乐可视化效果->下一预设"),
        ("previouspreset", "音乐可视化效果->上一预设"),
        ("lockpreset", "音乐可视化效果->锁定预设"),
        ("randompreset", "音乐可视化效果->随机预设"),
    ])),
    ("打开窗口", OrderedDict([
        ("SPECIAL_CUSTOM_WINDOW", "自定义窗口ID或名称"),
        ("activatewindow(home)", "主页"),
        ("activatewindow(settings)", "设置"),
        ("activatewindow(systeminfo)", "系统信息"),
        ("activatewindow(videos)", "视频"),
        ("activatewindow(music)", "音乐"),
        ("activatewindow(pictures)", "图片"),
        ("activatewindow(programs)", "插件/程序"),
        ("activatewindow(filemanager)", "文件管理器"),
        ("activatewindow(weather)", "天气"),
        ("activatewindow(favourites)", "收藏夹"),
        ("activatewindow(pvr)", "电视/广播"),
        ("activatewindow(videoosd)", "视频OSD"),
        ("activatewindow(musicosd)", "音乐OSD"),
        ("activatewindow(playerprocessinfo)", "播放器进程信息"),
        ("activatewindow(playersettings)", "播放器设置"),
        ("activatewindow(programssettings)", "插件设置"),
        ("activatewindow(infoprovidersettings)", "刮削器设置"),
        ("activatewindow(interfacesettings)", "界面设置"),
        ("activatewindow(systemsettings)", "系统设置"),
        ("activatewindow(mediasettings)", "媒体设置"),
        ("activatewindow(servicesettings)", "服务设置"),
        ("activatewindow(appearancesettings)", "外观设置"),
        ("activatewindow(peripheralsettings)", "外设设置"),
        ("activatewindow(libexportsettings)", "资料库导出设置"),
        ("activatewindow(pvrsettings)", "PVR 设置"),
        ("activatewindow(pvrrecordingsettings)", "PVR 录制设置"),
        ("activatewindow(gamesettings)", "游戏设置"),
        ("activatewindow(gameadvancedsettings)", "高级游戏设置"),
        ("activatewindow(gamecontrollers)", "游戏控制器"),
        ("activatewindow(gamevideofilter)", "游戏视频滤镜"),
        ("activatewindow(gamevideorotation)", "游戏视频旋转"),
        ("activatewindow(gameviewmode)", "游戏视图模式"),
        ("activatewindow(skinsettings)", "皮肤设置"),
        ("activatewindow(addonbrowser)", "插件浏览器"),
        ("activatewindow(addonsettings)", "插件设置"),
        ("activatewindow(profilesettings)", "配置文件设置"),
        ("activatewindow(locksettings)", "锁定设置"),
        ("activatewindow(contentsettings)", "内容设置"),
        ("activatewindow(profiles)", "配置文件"),
        ("activatewindow(testpattern)", "测试模式"),
        ("activatewindow(screencalibration)", "屏幕校准"),
        ("activatewindow(loginscreen)", "登录屏幕"),
        ("activatewindow(filebrowser)", "文件浏览器"),
        ("activatewindow(networksetup)", "网络设置"),
        ("activatewindow(accesspoints)", "接入点"),
        ("activatewindow(mediasource)", "媒体源"),
        ("activatewindow(startwindow)", "启动窗口"),
        ("activatewindow(favouritesbrowser)", "收藏浏览器"),
        ("activatewindow(contextmenu)", "上下文菜单"),
        ("activatewindow(mediafilter)", "媒体过滤器"),
        ("activatewindow(visualisationpresetlist)", "可视化预设列表"),
        ("activatewindow(smartplaylisteditor)", "智能播放列表编辑器"),
        ("activatewindow(smartplaylistrule)", "智能播放列表规则"),
        ("activatewindow(shutdownmenu)", "关机菜单"),
        ("activatewindow(fullscreeninfo)", "全屏信息"),
        ("activatewindow(subtitlesearch)", "字幕搜索"),
        ("activatewindow(screensaver)", "屏幕保护程序"),
        ("activatewindow(pictureinfo)", "图片信息"),
        ("activatewindow(addoninformation)", "插件信息"),
        ("activatewindow(musicplaylist)", "音乐当前队列(播放列表)"),
        ("activatewindow(musicplaylisteditor)", "音乐播放列表编辑器"),
        ("activatewindow(musicinformation)", "音乐信息"),
        ("activatewindow(songinformation)", "歌曲信息"),
        ("activatewindow(movieinformation)", "电影信息"),
        ("activatewindow(videomenu)", "视频菜单"),
        ("activatewindow(osdcmssettings)", "色彩管理设置"),
        ("activatewindow(osdsubtitlesettings)", "字幕设置"),
        ("activatewindow(videotimeseek)", "视频步进/时间跳转面板"),
        ("activatewindow(videobookmarks)", "视频书签管理器"),
        ("activatewindow(videoplaylist)", "视频当前队列(播放列表)"),
        ("activatewindow(pvrguideinfo)", "PVR 指南信息"),
        ("activatewindow(pvrrecordinginfo)", "PVR 录制信息"),
        ("activatewindow(pvrtimersetting)", "PVR 定时器设置"),
        ("activatewindow(pvrgroupmanager)", "PVR 组管理器(频道类别设定)"),
        ("activatewindow(pvrchannelmanager)", "PVR 频道管理器(隐藏/顺序设定)"),
        ("activatewindow(pvrguidesearch)", "PVR 指南搜索"),
        ("activatewindow(pvrchannelscan)", "PVR 频道扫描"),
        ("activatewindow(pvrupdateprogress)", "PVR 更新进度"),
        ("activatewindow(pvrosdchannels)", "PVR OSD 频道"),
        ("activatewindow(pvrchannelguide)", "PVR OSD 指南"),
        ("activatewindow(tvchannels)", "电视频道"),
        ("activatewindow(tvrecordings)", "电视录像"),
        ("activatewindow(tvguide)", "电视指南"),
        ("activatewindow(tvtimers)", "电视定时器"),
        ("activatewindow(tvsearch)", "电视搜索"),
        ("activatewindow(radiochannels)", "广播频道"),
        ("activatewindow(radiorecordings)", "广播录音"),
        ("activatewindow(radioguide)", "广播指南"),
        ("activatewindow(radiotimers)", "广播定时器"),
        ("activatewindow(radiotimerrules)", "广播定时器规则"),
        ("activatewindow(radiosearch)", "广播搜索"),
        ("activatewindow(pvrradiordsinfo)", "RDS 信息"),
        ("activatewindow(videos,movies)", "电影库(分类菜单)"),
        ("activatewindow(videos,movietitles)", "全部电影(直接显示影片墙)"),
        ("activatewindow(videos,tvshows)", "剧集库(分类菜单)"),
        ("activatewindow(videos,tvshowtitles)", "全部剧集(直接显示剧集墙)"),
        ("activatewindow(videos,musicvideos)", "音乐视频"),
        ("activatewindow(videos,recentlyaddedmovies)", "最近添加的电影"),
        ("activatewindow(videos,recentlyaddedepisodes)", "最近添加的剧集"),
        ("activatewindow(videos,recentlyaddedmusicvideos)", "最近添加的音乐视频"),
        ("activatewindow(games)", "游戏库"),
        ("activatewindow(gameosd)", "游戏 OSD"),
        ("activatewindow(gamepadinput)", "游戏手柄/遥控器输入映射页"),
        ("activatewindow(gamevolume)", "游戏音量"),
        ("activatewindow(managevideoversions)", "视频版本管理"),
        ("activatewindow(managevideoextras)", "视频花絮管理"),
        ("activatewindow(fullscreenvideo)", "全屏视频"),
        ("activatewindow(fullscreenlivetv)", "全屏直播电视"),
        ("activatewindow(fullscreenradio)", "全屏直播广播"),
        ("activatewindow(fullscreengame)", "全屏游戏"),
        ("activatewindow(virtualkeyboard)", "虚拟键盘"),
        ("activatewindow(playercontrols)", "播放控制器"),
        ("activatewindow(seekbar)", "进度条"),
        ("activatewindow(osdvideosettings)", "视频 OSD 设置"),
        ("activatewindow(osdaudiosettings)", "音频 OSD 设置"),
        ("activatewindow(visualisation)", "可视化"),
        ("activatewindow(slideshow)", "幻灯片")        
    ])),
    ("运行插件", "SPECIAL_RUN_ADDON"),
    ("自定义输入", None),
])

WINDOWS = OrderedDict([
    ("global", "全局"),
    ("fullscreenvideo", "全屏播放视频时"),
    ("fullscreenlivetv", "全屏播放电视直播时"),
    ("fullscreenradio", "全屏播放广播直播时"),
    ("fullscreengame", "全屏游戏时"),
    ("home", "在主界面/首页时"),
    ("programs", "在插件与程序界面时"),
    ("videos", "在视频库/目录时"),
    ("music", "在音乐库/目录时"),
    ("pictures", "在图片库/目录时"),
    ("pvr", "在电视/广播(PVR)界面时"),
    ("filemanager", "在文件管理器中时"),
    ("virtualkeyboard", "虚拟键盘弹出时"),
    ("playercontrols", "在播放控制器界面时"),
    ("seekbar", "出现播放跳转/进度条时"),
    ("videoosd", "视频OSD弹出时"),
    ("musicosd", "音乐OSD弹出时"),
    ("osdvideosettings", "视频设置菜单(OSD内)弹出时"),
    ("osdaudiosettings", "音轨与字幕设置(OSD内)弹出时"),
    ("visualisation", "在音乐可视化界面时"),
    ("slideshow", "在图片幻灯片播放时"),
])


def _log(msg, level=xbmc.LOGINFO):
    xbmc.log(f"[{ADDON_ID}] {msg}", level)


def _get_icon_path():
    return os.path.join(ADDON_PATH, "icon.png")


def _get_unique_backup_path(filepath):
    bak_path = filepath + '.bak'
    counter = 1
    while os.path.exists(bak_path):
        bak_path = filepath + f'.bak{counter}'
        counter += 1
    return bak_path


def _notification(message, title="RemoteSwitcher", duration=1000, sound=False):
    xbmcgui.Dialog().notification(title, message, _get_icon_path(), duration, sound)


def read_overwrite_keymap(filepath):
    """读取 overwrite xml，返回 [(context, action, keycode), ...]"""
    mappings = []
    if not os.path.exists(filepath):
        return mappings
        
    kb_name_to_code = {}
    rm_name_to_code = {}
    try:
        kb_path = os.path.join(ADDON_PATH, "data", "keyboard_mapping.json")
        if os.path.exists(kb_path):
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_name_to_code = json.load(f).get("name_to_code", {})
        rm_path = os.path.join(ADDON_PATH, "data", "remote_mapping.json")
        if os.path.exists(rm_path):
            with open(rm_path, "r", encoding="utf-8") as f:
                rm_name_to_code = json.load(f).get("name_to_code", {})
    except Exception as e:
        _log(f"加载mapping json失败以供读取: {e}")

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for context in root:
            for device in context:
                device_type = device.tag.lower()
                for mapping in device:
                    if mapping.tag.lower() == 'key':
                        keycode = mapping.get('id')
                    else:
                        name = mapping.tag.lower()
                        # resolve name to id based on device type
                        if device_type == 'keyboard' and name in kb_name_to_code:
                            keycode = str(kb_name_to_code[name])
                        elif device_type == 'remote' and name in rm_name_to_code:
                            keycode = str(rm_name_to_code[name])
                        else:
                            # fallback: search in both
                            keycode = str(kb_name_to_code.get(name, rm_name_to_code.get(name, name)))

                    if not keycode:
                        continue
                        
                    mod = mapping.get('mod', '')
                    action = mapping.text or ''
                    key_str = keycode
                    if mod:
                        key_str += ' + ' + mod
                    mappings.append((context.tag.lower(), action.strip().lower(), key_str))
    except Exception as e:
        _log(f"读取 overwrite keymap 失败: {e}", xbmc.LOGERROR)
    return mappings


def _indent_xml(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def write_overwrite_keymap(keymap, filepath):
    """将 [(context, action, keycode), ...] 写入 overwrite xml"""
    contexts = list(OrderedDict.fromkeys(c for c, a, k in keymap))

    builder = ET.TreeBuilder()
    builder.start("keymap", {})
    for context in contexts:
        builder.start(context, {})
        builder.start("keyboard", {})
        for c, a, k in keymap:
            if c == context:
                parts = k.split(' + ')
                attrs = {"id": parts[0]}
                if len(parts) > 1:
                    attrs["mod"] = parts[1]
                builder.start("key", attrs)
                builder.data(a)
                builder.end("key")
        builder.end("keyboard")
        builder.end(context)
    builder.end("keymap")
    element = builder.close()

    _indent_xml(element)
    
    tree = ET.ElementTree(element)
    tree.write(filepath, encoding='utf-8', xml_declaration=True)


class KeyListener(xbmcgui.WindowXMLDialog):
    TIMEOUT = 5

    def __new__(cls):
        gui_api = tuple(map(int, xbmcaddon.Addon(
            'xbmc.gui').getAddonInfo('version').split('.')))
        file_name = "DialogNotification.xml" if gui_api >= (5, 11, 0) else "DialogKaiToast.xml"
        return super(KeyListener, cls).__new__(cls, file_name, "")

    def __init__(self):
        self.key = None
        self.first_code = None
        self.closed = False
        import threading
        self.lock = threading.Lock()

    def onInit(self):
        # 尝试设置通知弹窗上的图标 (Kodi通知框图标通常为 Control 400)
        try:
            self.getControl(400).setImage(_get_icon_path())
        except Exception:
            pass

        try:
            self.getControl(401).addLabel("请按下要按键(可长按)...")
            self.getControl(402).addLabel(f"{self.TIMEOUT} 秒后超时")
        except AttributeError:
            self.getControl(401).setLabel("请按下要按键(可长按)...")
            self.getControl(402).setLabel(f"{self.TIMEOUT} 秒后超时")

    def onAction(self, action):
        code = action.getButtonCode()
        if code == 0:
            return

        MODIFIER_LONG = 16777216  # 0x01000000

        with self.lock:
            if self.closed:
                return

            if code & MODIFIER_LONG:
                base_code = code & ~MODIFIER_LONG
                self.key = str(base_code) + ' + longpress'
                self.close()
                return

            if self.first_code is None:
                self.first_code = code
                try:
                    # 尝试更新提示文字，捕捉长按意图
                    try:
                        self.getControl(401).setLabel("已记录，按住可识别为长按")
                    except AttributeError:
                        self.getControl(401).reset()
                        self.getControl(401).addLabel("已记录，按住可识别为长按")
                except Exception as e:
                    _log(f"更新提示文字失败: {e}", xbmc.LOGERROR)
                
                # 0.5s 内如果 Kodi 没有发送带有长按修饰符的事件，则算作短按
                self.short_press_timer = Timer(1, self._finalize_short_press)
                self.short_press_timer.start()

    def _finalize_short_press(self):
        with self.lock:
            if not self.closed:
                self.key = str(self.first_code)
                self.close()

    def close(self):
        self.closed = True
        if hasattr(self, 'short_press_timer'):
            self.short_press_timer.cancel()
        super(KeyListener, self).close()

    @staticmethod
    def record_key():
        dialog = KeyListener()
        timeout = Timer(KeyListener.TIMEOUT, dialog.close)
        timeout.start()
        dialog.doModal()
        timeout.cancel()
        key = dialog.key
        del dialog
        return key


def _record_key_with_longpress():
    """捕获按键(已支持自动长按识别)，返回 keycode 字符串或 None"""
    return KeyListener.record_key()


def _select_action():
    """选择一个 action，返回 action 字符串或 None"""
    while True:
        categories = list(ACTIONS.keys())
        idx = xbmcgui.Dialog().select("选择动作分类", categories)
        if idx == -1:
            return None

        category = categories[idx]

        if ACTIONS[category] == "SPECIAL_RUN_ADDON":
            import json
            addons = []
            for addon_type in ['xbmc.python.pluginsource', 'xbmc.python.script']:
                query = {
                    "jsonrpc": "2.0",
                    "method": "Addons.GetAddons",
                    "params": {"type": addon_type, "properties": ["name", "enabled"]},
                    "id": 1
                }
                try:
                    resp = xbmc.executeJSONRPC(json.dumps(query))
                    data = json.loads(resp)
                    if 'addons' in data.get('result', {}):
                        addons.extend([a for a in data['result']['addons'] if a.get('enabled')])
                except Exception:
                    pass
            
            if not addons:
                xbmcgui.Dialog().ok("提示", "未找到任何支持运行的插件")
                continue
                
            addons.sort(key=lambda x: x.get('name', x['addonid']).lower())
            labels = [a.get('name', a['addonid']) for a in addons]
            
            idx2 = xbmcgui.Dialog().select("选择要运行的插件", labels)
            if idx2 == -1:
                continue
                
            return f"RunAddon({addons[idx2]['addonid']})"

        if ACTIONS[category] is None:
            # 自定义输入
            action = xbmcgui.Dialog().input("输入 Kodi Action 名称")
            if not action:
                continue
            return action.strip()

        actions = ACTIONS[category]
        labels = [f"{name} ({action_id})" for action_id, name in actions.items()]
        idx2 = xbmcgui.Dialog().select("选择动作", labels)
        if idx2 == -1:
            continue
        selected_key = list(actions.keys())[idx2]
        if selected_key == "SPECIAL_CUSTOM_WINDOW":
            window_id = xbmcgui.Dialog().input("输入窗口名称或ID")
            if not window_id:
                continue
            return f"activatewindow({window_id.strip()})"
        return selected_key


def _select_window():
    """选择一个窗口上下文，返回 context 字符串或 None"""
    labels = list(WINDOWS.values()) + ["指定窗口ID"]
    idx = xbmcgui.Dialog().select("选择生效范围", labels)
    if idx == -1:
        return None
    if idx == len(WINDOWS):
        window_id = xbmcgui.Dialog().input("输入窗口ID (数字)")
        if not window_id or not window_id.strip().isdigit():
            return None
        return f"Window{window_id.strip()}"
    return list(WINDOWS.keys())[idx]


def _format_mapping(context, action, keycode):
    window_name = WINDOWS.get(context, context)
    if context.lower().startswith('window') and context[6:].isdigit():
        window_name = f"在{context[6:]}窗口时"
    press_type = " [长按]" if 'longpress' in keycode else " [短按]"
    display_key = keycode.replace(' + longpress', '')

    names = ""
    try:
        if not hasattr(_format_mapping, "kb_map"):
            _format_mapping.kb_map = {}
            _format_mapping.rm_map = {}
            kb_path = os.path.join(ADDON_PATH, "data", "keyboard_mapping.json")
            if os.path.exists(kb_path):
                with open(kb_path, "r", encoding="utf-8") as f:
                    _format_mapping.kb_map = json.load(f).get("code_to_names", {})
            rm_path = os.path.join(ADDON_PATH, "data", "remote_mapping.json")
            if os.path.exists(rm_path):
                with open(rm_path, "r", encoding="utf-8") as f:
                    _format_mapping.rm_map = json.load(f).get("code_to_names", {})
                    
        name_list = _format_mapping.kb_map.get(display_key) or _format_mapping.rm_map.get(display_key)
        if name_list:
            names = f"[{','.join(name_list)}]"
    except Exception as e:
        _log(f"读取mapping json失败: {e}")
        
    return f"[{window_name}] {display_key}{names}{press_type} -> {action}"


def _save_to_disk(keymap, overwrite_path):
    """辅助函数：实时保存内存到磁盘"""
    if not keymap:
        if os.path.exists(overwrite_path):
            os.remove(overwrite_path)
    else:
        write_overwrite_keymap(keymap, overwrite_path)


def manage_custom_keymap(overwrite_path, remote_name):
    """自定义按键编辑器主菜单"""
    keymap = read_overwrite_keymap(overwrite_path)
    has_unapplied_changes = False

    while True:
        apply_label = "应用修改 (*)" if has_unapplied_changes else "应用修改"
        ops = ["编辑按键映射", apply_label, "移除该映射文件"]
        title = f"自定义按键 - {remote_name}"
            
        idx = xbmcgui.Dialog().select(title, ops)
        
        if idx == -1:
            break
            
        elif idx == 0:
            # 进入编辑主循环
            if _edit_custom_keymap_loop(keymap, overwrite_path):
                has_unapplied_changes = True
                
        elif idx == 1:
            # 应用
            xbmc.executebuiltin('Action(ReloadKeymaps)')
            has_unapplied_changes = False
            _notification("已应用最新配置", title="成功")
            
        elif idx == 2:
            # 移除自定义映射
            if xbmcgui.Dialog().yesno('确认移除', f"确定要移除 {remote_name} 的自定义按键吗？"):
                keymap.clear()
                if os.path.exists(overwrite_path):
                    _save_to_disk(keymap, overwrite_path)
                    has_unapplied_changes = True
                    _notification("已移除磁盘文件，请点击应用使其生效", title="成功")
                else:
                    _notification(f"{remote_name} 没有已部署的自定义按键", title="提示")

def _edit_custom_keymap_loop(keymap, overwrite_path):
    """自定义按键编辑器内容循环"""
    changed = False
    while True:
        # 构建菜单
        menu = ["[添加新按键映射]"]
        
        for c, a, k in keymap:
            menu.append(_format_mapping(c, a, k))

        title = f"编辑自定义按键 ({os.path.basename(overwrite_path)})"
            
        idx = xbmcgui.Dialog().select(title, menu)

        if idx == -1:
            return changed
            
        elif idx == 0:
            # 添加新映射：先选范围 → 选动作 → 最后按键
            window = _select_window()
            if window is None:
                continue

            action = _select_action()
            if action is None:
                continue

            # _notification("请按下遥控器按键...", title="等待按键", duration=3000)
            keycode = _record_key_with_longpress()
            if keycode is None:
                _notification("未捕获到按键", title="取消")
                continue

            keymap.append((window, action, keycode))
            _save_to_disk(keymap, overwrite_path)
            changed = True
            
        else:
            # 编辑/删除已有映射
            mapping_idx = idx - 1
            c, a, k = keymap[mapping_idx]
            choice = xbmcgui.Dialog().select(
                _format_mapping(c, a, k),
                ["修改按键", "修改生效范围", "修改动作", "删除此按键"]
            )
            if choice == 0:
                # _notification("请按下新按键...", title="等待按键", duration=3000)
                newkey = _record_key_with_longpress()
                if newkey:
                    keymap[mapping_idx] = (c, a, newkey)
                    _save_to_disk(keymap, overwrite_path)
                    changed = True
            elif choice == 1:
                new_window = _select_window()
                if new_window is not None:
                    keymap[mapping_idx] = (new_window, a, k)
                    _save_to_disk(keymap, overwrite_path)
                    changed = True
            elif choice == 2:
                new_action = _select_action()
                if new_action is not None:
                    keymap[mapping_idx] = (c, new_action, k)
                    _save_to_disk(keymap, overwrite_path)
                    changed = True
            elif choice == 3:
                keymap.pop(mapping_idx)
                _save_to_disk(keymap, overwrite_path)
                changed = True
