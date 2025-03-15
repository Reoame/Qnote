@echo off
echo Qnote Installation Script
echo =========================

:: 设置安装路径
set "INSTALL_DIR=%APPDATA%\Qnote"

:: 创建安装目录
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

:: 复制可执行文件到安装目录
copy dist\Qnote.exe "%INSTALL_DIR%"

:: 创建快捷方式
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Qnote.lnk"
set "TARGET=%INSTALL_DIR%\Qnote.exe"
set "WORKINGDIR=%INSTALL_DIR%"

:: 使用WScript.Shell创建快捷方式
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%WORKINGDIR%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

:: 运行脚本创建快捷方式
cscript CreateShortcut.vbs
del CreateShortcut.vbs

echo Installation complete!
pause