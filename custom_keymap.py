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

from utils import custom_select,log,sync_reload_keymaps

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

ACTIONS = OrderedDict([
    ("常用", OrderedDict([
        ("playerprocessinfo", "打开播放器进程信息页面(音视频解码格式,码率等)"),
        ("activatewindow(settings)", "打开设置页面"),
        ("playpause", "播放/暂停"),
        ("skipnext", "播放下一个"),
        ("skipprevious", "播放上一个"),
        ("stop", "停止播放"),
        ("fastforward", "快进"),
        ("rewind", "快退"),
        ("activatewindow(playercontrols)", "打开播放控制器"),
        ("fullscreen", "在主页与全屏播放界面间切换"),
        ("screenshot", "截屏"),
        ("info", "显示项目信息"),
        ("contextmenu", "打开选项菜单(上下文/右键菜单)"),
        ("audiodelayminus", "音频延迟减少"),
        ("audiodelayplus", "音频延迟增加"),
        ("subtitledelayminus", "字幕延迟减少"),
        ("subtitledelayplus", "字幕延迟增加"),
        ("updatelibrary(video)", "更新视频库"),
        ("activatewindow(shutdownmenu)", "打开关机菜单"),
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
        ("RunScript(plugin.video.filteredmovies, ?mode=restart_linux_kodi)", "Linux(coreelec)上强制重启kodi"),
        ("RunScript(plugin.video.filteredmovies, ?mode=reboot_from_nand)", "coreelec上重启到安卓系统"),
        ("RunScript(plugin.video.filteredmovies, ?mode=set_vs10_mode)", "coreelec cpm/avdvplus系上循环切换VS10转码模式"),
        ("RunScript(plugin.video.filteredmovies, ?mode=set_vs10_mode&target_mode=vs10.dv)", "coreelec cpm/avdvplus系上使用VS10转码为 杜比视界"),
        ("RunScript(plugin.video.filteredmovies, ?mode=set_vs10_mode&target_mode=vs10.hdr10)", "coreelec cpm/avdvplus系上使用VS10转码为 HDR10"),
        ("RunScript(plugin.video.filteredmovies, ?mode=set_vs10_mode&target_mode=vs10.sdr)", "coreelec cpm/avdvplus系上使用VS10转码为 SDR"),
        ("RunScript(plugin.video.filteredmovies, ?mode=set_vs10_mode&target_mode=vs10.original)", "coreelec cpm/avdvplus系上关闭VS10转码"),
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
        ("contextmenu", "打开选项菜单(上下文/右键菜单)"),
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
        ("fullscreen", "在主页与全屏播放界面间切换"),
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
        ("playercontrol(repeat)", "切换循环播放模式(仅播放音乐时有效)"),
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
        ("playerprocessinfo", "打开播放器进程信息页面(音视频解码格式,码率等)"),
        ("playerdebug", "打开内核播放器调试信息页面(A-V音画同步,队列及丢帧)"),
        ("playerdebugvideo", "打开底层视频渲染器调试信息页面(OpenGL/DX色彩与送显)"),
        ("screenshot", "截屏"),
        ("reloadkeymaps", "重新加载按键映射文件(使keymaps目录下的修改生效)"),
        ("increasepar", "拉长画面像素(增加PAR比例)"),
        ("decreasepar", "压扁画面像素(减少PAR比例)"),
        ("nextresolution", "[视频校准专属] 下一分辨率"),
        ("nextcalibration", "[视频校准专属] 下一校准步骤"),
        ("resetcalibration", "[视频校准专属] 重置校准参数"),
        ("showpreset", "音乐可视化效果->显示预设"),
        ("presetlist", "音乐可视化效果->预设列表"),
        ("nextpreset", "音乐可视化效果->下一预设"),
        ("previouspreset", "音乐可视化效果->上一预设"),
        ("lockpreset", "音乐可视化效果->锁定预设"),
        ("randompreset", "音乐可视化效果->随机预设"),
    ])),
    ("打开窗口", OrderedDict([
        ("SPECIAL_CUSTOM_WINDOW", "自定义窗口ID或名称"),
        ("activatewindow(home)", "打开主页"),
        ("activatewindow(settings)", "打开设置页面"),
        ("activatewindow(systeminfo)", "打开系统信息页面"),
        ("activatewindow(videos)", "打开视频页面"),
        ("activatewindow(music)", "打开音乐页面"),
        ("activatewindow(pictures)", "打开图片页面"),
        ("activatewindow(programs)", "打开插件/程序页面"),
        ("activatewindow(filemanager)", "打开文件管理器页面"),
        ("activatewindow(weather)", "打开天气页面"),
        ("activatewindow(favouritesbrowser)", "浏览收藏页面"),
        ("activatewindow(addonbrowser)", "浏览插件页面"),
        ("activatewindow(playercontrols)", "打开播放控制器页面"),
        ("activatewindow(pvr)", "打开电视/广播页面"),
        ("activatewindow(videoosd)", "打开视频OSD页面"),
        ("activatewindow(musicosd)", "打开音乐OSD页面"),
        ("activatewindow(videos,movies)", "打开电影库(分类菜单)页面"),
        ("activatewindow(videos,movietitles)", "打开全部电影(直接显示影片墙)页面"),
        ("activatewindow(videos,tvshows)", "打开剧集库(分类菜单)页面"),
        ("activatewindow(videos,tvshowtitles)", "打开全部剧集(直接显示剧集墙)页面"),
        ("activatewindow(playerprocessinfo)", "打开播放器进程信息页面"),
        ("activatewindow(playersettings)", "打开播放器设置页面"),
        ("activatewindow(programssettings)", "打开插件设置页面"),
        ("activatewindow(infoprovidersettings)", "打开刮削器设置页面"),
        ("activatewindow(interfacesettings)", "打开界面设置页面"),
        ("activatewindow(systemsettings)", "打开系统设置页面"),
        ("activatewindow(mediasettings)", "打开媒体设置页面"),
        ("activatewindow(servicesettings)", "打开服务设置页面"),
        ("activatewindow(appearancesettings)", "打开外观设置页面"),
        ("activatewindow(peripheralsettings)", "打开外设设置页面"),
        ("activatewindow(libexportsettings)", "打开资料库导出设置页面"),
        ("activatewindow(pvrsettings)", "打开PVR 设置页面"),
        ("activatewindow(pvrrecordingsettings)", "打开PVR 录制设置页面"),
        ("activatewindow(gamesettings)", "打开游戏设置页面"),
        ("activatewindow(gameadvancedsettings)", "打开高级游戏设置页面"),
        ("activatewindow(gamecontrollers)", "打开游戏控制器页面"),
        ("activatewindow(gamevideofilter)", "打开游戏视频滤镜页面"),
        ("activatewindow(gamevideorotation)", "打开游戏视频旋转页面"),
        ("activatewindow(gameviewmode)", "打开游戏视图模式页面"),
        ("activatewindow(skinsettings)", "打开皮肤设置页面"),
        ("activatewindow(addonsettings)", "打开插件设置页面"),
        ("activatewindow(profilesettings)", "打开配置文件设置页面"),
        ("activatewindow(locksettings)", "打开锁定设置页面"),
        ("activatewindow(contentsettings)", "打开内容设置页面"),
        ("activatewindow(profiles)", "打开配置文件页面"),
        ("activatewindow(testpattern)", "打开测试模式页面"),
        ("activatewindow(screencalibration)", "打开屏幕校准页面"),
        ("activatewindow(loginscreen)", "打开登录屏幕页面"),
        ("activatewindow(filebrowser)", "打开文件浏览器页面"),
        ("activatewindow(networksetup)", "打开网络设置页面"),
        ("activatewindow(accesspoints)", "打开接入点页面"),
        ("activatewindow(mediasource)", "打开媒体源页面"),
        ("activatewindow(startwindow)", "打开启动窗口页面"),
        ("activatewindow(contextmenu)", "打开上下文菜单页面"),
        ("activatewindow(mediafilter)", "打开媒体过滤器页面"),
        ("activatewindow(visualisationpresetlist)", "打开可视化预设列表页面"),
        ("activatewindow(smartplaylisteditor)", "打开智能播放列表编辑器页面"),
        ("activatewindow(smartplaylistrule)", "打开智能播放列表规则页面"),
        ("activatewindow(shutdownmenu)", "打开关机菜单页面"),
        ("activatewindow(fullscreeninfo)", "打开全屏信息页面"),
        ("activatewindow(subtitlesearch)", "打开字幕搜索页面"),
        ("activatewindow(screensaver)", "打开屏幕保护程序页面"),
        ("activatewindow(pictureinfo)", "打开图片信息页面"),
        ("activatewindow(addoninformation)", "打开插件信息页面"),
        ("activatewindow(musicplaylist)", "打开音乐当前队列(播放列表)页面"),
        ("activatewindow(musicplaylisteditor)", "打开音乐播放列表编辑器页面"),
        ("activatewindow(musicinformation)", "打开音乐信息页面"),
        ("activatewindow(songinformation)", "打开歌曲信息页面"),
        ("activatewindow(movieinformation)", "打开电影信息页面"),
        ("activatewindow(videomenu)", "打开视频菜单页面"),
        ("activatewindow(osdcmssettings)", "打开色彩管理设置页面"),
        ("activatewindow(osdsubtitlesettings)", "打开字幕设置页面"),
        ("activatewindow(videotimeseek)", "打开视频步进/时间跳转面板页面"),
        ("activatewindow(videobookmarks)", "打开视频书签管理器页面"),
        ("activatewindow(videoplaylist)", "打开视频当前队列(播放列表)页面"),
        ("activatewindow(pvrguideinfo)", "打开PVR 指南信息页面"),
        ("activatewindow(pvrrecordinginfo)", "打开PVR 录制信息页面"),
        ("activatewindow(pvrtimersetting)", "打开PVR 定时器设置页面"),
        ("activatewindow(pvrgroupmanager)", "打开PVR 组管理器(频道类别设定)页面"),
        ("activatewindow(pvrchannelmanager)", "打开PVR 频道管理器(隐藏/顺序设定)页面"),
        ("activatewindow(pvrguidesearch)", "打开PVR 指南搜索页面"),
        ("activatewindow(pvrchannelscan)", "打开PVR 频道扫描页面"),
        ("activatewindow(pvrupdateprogress)", "打开PVR 更新进度页面"),
        ("activatewindow(pvrosdchannels)", "打开PVR OSD 频道页面"),
        ("activatewindow(pvrchannelguide)", "打开PVR OSD 指南页面"),
        ("activatewindow(tvchannels)", "打开电视频道页面"),
        ("activatewindow(tvrecordings)", "打开电视录像页面"),
        ("activatewindow(tvguide)", "打开电视指南页面"),
        ("activatewindow(tvtimers)", "打开电视定时器页面"),
        ("activatewindow(tvsearch)", "打开电视搜索页面"),
        ("activatewindow(radiochannels)", "打开广播频道页面"),
        ("activatewindow(radiorecordings)", "打开广播录音页面"),
        ("activatewindow(radioguide)", "打开广播指南页面"),
        ("activatewindow(radiotimers)", "打开广播定时器页面"),
        ("activatewindow(radiotimerrules)", "打开广播定时器规则页面"),
        ("activatewindow(radiosearch)", "打开广播搜索页面"),
        ("activatewindow(pvrradiordsinfo)", "打开RDS 信息页面"),
        ("activatewindow(videos,musicvideos)", "打开音乐视频库页面"),
        ("activatewindow(videos,recentlyaddedmovies)", "打开最近添加的电影页面"),
        ("activatewindow(videos,recentlyaddedepisodes)", "打开最近添加的剧集页面"),
        ("activatewindow(videos,recentlyaddedmusicvideos)", "打开最近添加的音乐视频页面"),
        ("activatewindow(games)", "打开游戏库页面"),
        ("activatewindow(gameosd)", "打开游戏 OSD 页面"),
        ("activatewindow(gamepadinput)", "打开游戏手柄/遥控器输入映射页面"),
        ("activatewindow(gamevolume)", "打开游戏音量页面"),
        ("activatewindow(managevideoversions)", "打开视频版本管理页面"),
        ("activatewindow(managevideoextras)", "打开视频花絮管理页面"),
        ("activatewindow(fullscreenvideo)", "打开全屏视频页面"),
        ("activatewindow(fullscreenlivetv)", "打开全屏直播电视页面"),
        ("activatewindow(fullscreenradio)", "打开全屏直播广播页面"),
        ("activatewindow(fullscreengame)", "打开全屏游戏页面"),
        ("activatewindow(virtualkeyboard)", "打开虚拟键盘页面"),
        ("activatewindow(seekbar)", "打开进度条组件"),
        ("activatewindow(osdvideosettings)", "打开视频 OSD 设置页面"),
        ("activatewindow(osdaudiosettings)", "打开音频 OSD 设置页面"),
        ("activatewindow(visualisation)", "打开音乐可视化页面"),
        ("activatewindow(slideshow)", "打开幻灯片页面"),
        ("activatewindow(favourites)", "打开旧版收藏夹页面(kodi20+请使用浏览收藏页面)")      
    ])),
    ("运行插件", "SPECIAL_RUN_ADDON"),
    ("自定义输入", None),
])

WINDOWS = OrderedDict([
    ("global", "全局"),
    ("fullscreenvideo", "全屏播放视频时"),
    ("fullscreenlivetv", "全屏播放电视时"),
    ("fullscreenradio", "全屏播放广播时"),
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

JOYSTICK_FEATURES = OrderedDict([
    ("a", "A (底部)"),
    ("b", "B (右侧)"),
    ("x", "X (左侧)"),
    ("y", "Y (顶部)"),
    ("start", "开始"),
    ("back", "返回"),
    ("guide", "指南"),
    ("up", "十字键 上"),
    ("down", "十字键 下"),
    ("left", "十字键 左"),
    ("right", "十字键 右"),
    ("leftbumper", "左肩键 LB"),
    ("rightbumper", "右肩键 RB"),
    ("lefttrigger", "左扳机 LT"),
    ("righttrigger", "右扳机 RT"),
    ("leftthumb", "左摇杆按下"),
    ("rightthumb", "右摇杆按下"),
    ("leftstick@up", "左摇杆 上"),
    ("leftstick@down", "左摇杆 下"),
    ("leftstick@left", "左摇杆 左"),
    ("leftstick@right", "左摇杆 右"),
    ("rightstick@up", "右摇杆 上"),
    ("rightstick@down", "右摇杆 下"),
    ("rightstick@left", "右摇杆 左"),
    ("rightstick@right", "右摇杆 右"),
])


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
        log(f"加载mapping json失败以供读取: {e}")

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        for context in root:
            for device in context:
                device_type = device.tag.lower()
                if device_type == 'joystick':
                    for mapping in device:
                        feature_name = mapping.tag.lower()
                        holdtime = mapping.get('holdtime', '')
                        direction = mapping.get('direction', '')
                        action = mapping.text or ''
                        key_str = f"joystick:{feature_name}"
                        if direction:
                            key_str = f"joystick:{feature_name}@{direction}"
                        if holdtime:
                            key_str += f" + holdtime={holdtime}"
                        mappings.append((context.tag.lower(), action.strip().lower(), key_str))
                    continue
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
        log(f"读取 overwrite keymap 失败: {e}", xbmc.LOGERROR)
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

        kb_entries = [(c, a, k) for c, a, k in keymap if c == context and not k.startswith('joystick:')]
        if kb_entries:
            builder.start("keyboard", {})
            for c, a, k in kb_entries:
                parts = k.split(' + ')
                attrs = {"id": parts[0]}
                if len(parts) > 1:
                    attrs["mod"] = parts[1]
                builder.start("key", attrs)
                builder.data(a)
                builder.end("key")
            builder.end("keyboard")

        joy_entries = [(c, a, k) for c, a, k in keymap if c == context and k.startswith('joystick:')]
        if joy_entries:
            builder.start("joystick", {"profile": "game.controller.default"})
            for c, a, k in joy_entries:
                feature = k[len('joystick:'):]
                parts = feature.split(' + ')
                feature_part = parts[0]
                attrs = {}
                if '@' in feature_part:
                    feature_name, direction = feature_part.split('@', 1)
                    attrs['direction'] = direction
                else:
                    feature_name = feature_part
                if len(parts) > 1 and parts[1].startswith('holdtime='):
                    attrs['holdtime'] = parts[1].split('=', 1)[1]
                builder.start(feature_name, attrs)
                builder.data(a)
                builder.end(feature_name)
            builder.end("joystick")

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

    def onInit(self):
        try:
            self.getControl(400).setImage(_get_icon_path())
        except Exception:
            pass

        try:
            self.getControl(401).addLabel("请按下要绑定的按键...")
            self.getControl(402).addLabel(f"{self.TIMEOUT} 秒后超时")
        except AttributeError:
            self.getControl(401).setLabel("请按下要绑定的按键...")
            self.getControl(402).setLabel(f"{self.TIMEOUT} 秒后超时")

    def onAction(self, action):
        code = action.getButtonCode()
        if code == 0:
            return
        # 去掉长按修饰符，只取基础按键码
        MODIFIER_LONG = 0x01000000
        self.key = str(code & ~MODIFIER_LONG)
        self.close()

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
    """捕获按键，然后询问短按/长按，返回 keycode 字符串或 None"""
    key = KeyListener.record_key()
    if key is None:
        return None
    lp = xbmcgui.Dialog().yesno("选择按键类型", "选择短按触发或长按触发,遥控器的某些按键可能不支持长按！", yeslabel="长按", nolabel="短按")
    if lp:
        key += ' + longpress'
    return key


def _record_joystick_key():
    """选择手柄按键，返回 joystick:feature 或 joystick:feature + holdtime=500"""
    features = list(JOYSTICK_FEATURES.keys())
    labels = [f"{name} ({fid})" for fid, name in JOYSTICK_FEATURES.items()]
    idx = custom_select("选择手柄按键", labels)
    if idx == -1:
        return None
    feature = features[idx]
    lp = xbmcgui.Dialog().yesno("选择按键类型", "选择短按触发或长按触发", yeslabel="长按", nolabel="短按")
    key_str = f"joystick:{feature}"
    if lp:
        key_str += " + holdtime=500"
    return key_str


def _record_key_choose_type(controller_type=''):
    """选择输入设备类型并录入按键"""
    if controller_type == 'gamepad':
        return _record_joystick_key()
    elif controller_type in ('remote', 'keyboard'):
        return _record_key_with_longpress()
    # controller_type未指定时，弹窗选择
    idx = custom_select("选择输入设备", ["遥控器/键盘", "手柄(Joystick)"])
    if idx == -1:
        return None
    if idx == 0:
        return _record_key_with_longpress()
    return _record_joystick_key()


def _select_action():
    """选择一个 action，返回 action 字符串或 None"""
    while True:
        categories = list(ACTIONS.keys())
        idx = custom_select("选择动作分类", categories)
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

            idx2 = custom_select("选择要运行的插件", labels)
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
        title = "选择窗口" if category == "打开窗口" else "选择动作"
        idx2 = custom_select(title, labels)
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
    idx = custom_select("选择生效范围", labels)
    if idx == -1:
        return None
    if idx == len(WINDOWS):
        window_id = xbmcgui.Dialog().input("输入窗口ID (数字)")
        if not window_id or not window_id.strip().isdigit():
            return None
        return f"Window{window_id.strip()}"
    return list(WINDOWS.keys())[idx]


def _translate_action(action):
    """将 action 字符串翻译为中文描述"""
    if not action:
        return "擦除预设映射 (穿透到系统)"
    action_lower = action.strip().lower()
    for category, actions in ACTIONS.items():
        if isinstance(actions, OrderedDict):
            for action_id, desc in actions.items():
                if action_id.lower() == action_lower:
                    return desc
    import re
    m = re.match(r'activatewindow\((.+)\)', action_lower)
    if m:
        return f"打开页面({m.group(1)})"
    m = re.match(r'runaddon\((.+)\)', action_lower)
    if m:
        return f"运行插件({m.group(1)})"
    return action


def _format_mapping(context, action, keycode):
    window_name = WINDOWS.get(context, context)
    if context.lower().startswith('window') and context[6:].isdigit():
        window_name = f"在{context[6:]}窗口时"

    if keycode.startswith('joystick:'):
        feature = keycode[len('joystick:'):]
        parts = feature.split(' + ')
        feature_part = parts[0]
        press_type = " [长按]" if len(parts) > 1 else " [短按]"
        joy_label = JOYSTICK_FEATURES.get(feature_part, feature_part)
        key_display = f"手柄:[COLOR yellow]{joy_label}[/COLOR]"
    else:
        press_type = " [长按]" if 'longpress' in keycode else " [短按]"
        display_key = keycode.replace(' + longpress', '')

        key_display = ""
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
                key_display = f"{display_key}[[COLOR  yellow]{','.join(name_list)}[/COLOR]]"
            else:
                key_display = display_key
        except Exception as e:
            log(f"读取mapping json失败: {e}")
            key_display = display_key

    action_display = _translate_action(action)
    if action_display != action:
        action_display = f"[COLOR  yellow]{action_display}[/COLOR] ({action})"
    return f"[[COLOR  yellow]{window_name}[/COLOR]] {key_display}{press_type} -> {action_display}"


def _save_to_disk(keymap, overwrite_path):
    """辅助函数：实时保存内存到磁盘并立刻生效"""
    
    if not keymap:
        if os.path.exists(overwrite_path):
            os.remove(overwrite_path)
    else:
        write_overwrite_keymap(keymap, overwrite_path)
    sync_reload_keymaps()


def manage_custom_keymap(overwrite_path, remote_name, controller_type=''):
    """自定义按键编辑器主菜单"""
    if not controller_type:
        idx = custom_select("选择该文件对应的输入设备类型", ["遥控器/键盘", "手柄(Joystick)"])
        if idx == -1:
            return
        controller_type = 'remote' if idx == 0 else 'gamepad'
    keymap = read_overwrite_keymap(overwrite_path)
    last_idx = -1

    while True:
        ops = ["编辑按键映射", "移除该映射文件"]
        title = f"自定义按键 - {remote_name}"

        idx = custom_select(title, ops, preselect=max(last_idx, 0))

        if idx == -1:
            break
        last_idx = idx

        if idx == 0:
            # 进入编辑主循环
            _edit_custom_keymap_loop(keymap, overwrite_path, controller_type)

        elif idx == 1:
            # 移除自定义映射
            if xbmcgui.Dialog().yesno('确认移除', f"确定要移除 {remote_name} 的自定义按键吗？"):
                keymap.clear()
                if os.path.exists(overwrite_path):
                    _save_to_disk(keymap, overwrite_path)
                    _notification("已移除磁盘文件并生效", title="成功")
                else:
                    _notification(f"{remote_name} 没有已部署的自定义按键", title="提示")
                break

def _edit_custom_keymap_loop(keymap, overwrite_path, controller_type=''):
    """自定义按键编辑器内容循环"""
    changed = False
    last_idx = -1
    while True:
        # 构建菜单
        menu = ["[添加新按键映射]"]
        
        for c, a, k in keymap:
            menu.append(_format_mapping(c, a, k))

        title = f"编辑自定义按键 ({os.path.basename(overwrite_path)})"
            
        idx = custom_select(title, menu,
                            preselect=min(max(last_idx, 0), len(menu) - 1))

        if idx == -1:
            return changed
        last_idx = idx
            
        if idx == 0:
            # 添加新映射：先选范围 → 选动作 → 最后按键
            window = _select_window()
            if window is None:
                continue

            action = _select_action()
            if action is None:
                continue

            keycode = _record_key_choose_type(controller_type)
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
            choice = custom_select(
                _format_mapping(c, a, k),
                ["修改按键", "修改生效范围", "修改动作", "删除此按键"]
            )
            if choice == 0:
                newkey = _record_key_choose_type(controller_type)
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
