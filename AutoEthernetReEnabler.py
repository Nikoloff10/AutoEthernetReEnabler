import subprocess
import time
import os
import winreg as reg
import ctypes
import sys


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()


def disable_adapter(adapter_name):
    subprocess.run(f'netsh interface set interface "{adapter_name}" admin=disable', shell=True)
    print(f"Disabled {adapter_name}")


def enable_adapter(adapter_name):
    subprocess.run(f'netsh interface set interface "{adapter_name}" admin=enable', shell=True)
    print(f"Enabled {adapter_name}")


def add_to_startup(file_path):
    key = reg.HKEY_CURRENT_USER
    key_value = f'Software\\Microsoft\\Windows\\CurrentVersion\\Run'
    open_key = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
    reg.SetValueEx(open_key, "AutoEthernetReEnabler", 0, reg.REG_SZ, file_path)
    reg.CloseKey(open_key)


def remove_old_exe(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Removed old executable: {file_path}")
    else:
        print(f"No old executable found at: {file_path}")


if __name__ == "__main__":
    run_as_admin()

    adapter_name = "Ethernet"
    disable_adapter(adapter_name)
    time.sleep(7)
    enable_adapter(adapter_name)
    time.sleep(7)

    exe_path = os.path.join(os.getcwd(), 'dist', 'AutoEthernetReEnabler.exe')
    remove_old_exe(exe_path)
    add_to_startup(exe_path)