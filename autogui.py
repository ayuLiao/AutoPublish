import pyautogui
import pyperclip
import platform

sysinfo = platform.platform()
pyautogui.PAUSE = 0.5  # 设置每个动作0.5s

def paste():
    if 'windows' in sysinfo.lower() or 'linux' in sysinfo.lower():
        pyautogui.hotkey('ctrl', 'v')
    else:
        # Mac OS
        pyautogui.hotkey('command', 'v')


def copypaste(content):
    ''' copy and paste '''
    pyperclip.copy(content)
    paste()


def copy():
    if 'windows' in sysinfo.lower() or 'linux' in sysinfo.lower():
        pyautogui.hotkey('ctrl', 'c')
    else:
        # Mac OS
        pyautogui.hotkey('command', 'c')


def copyall():
    ''' 全选 浏览器中的内容 '''
    if 'windows' in sysinfo.lower() or 'linux' in sysinfo.lower():
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
    else:
        # Mac OS
        pyautogui.hotkey('command', 'a')
        pyautogui.hotkey('command', 'c')
