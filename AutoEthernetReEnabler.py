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
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
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
    reg.SetValueEx(open_key, "AutoEthernetReEnabler.exe", 0, reg.REG_SZ, file_path)
    reg.CloseKey(open_key)
    print(f"Added {file_path} to startup")

def remove_old_exe(file_path):
    retries = 3
    for i in range(retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed old executable: {file_path}")
            else:
                print(f"No old executable found at: {file_path}")
            break
        except PermissionError as e:
            print(f"Attempt {i+1} to remove old executable failed: {e}")
            time.sleep(1)
    else:
        print(f"Failed to remove old executable after {retries} attempts")

def add_defender_exclusion(file_path):
    ps_script = f"""
    Add-MpPreference -ExclusionPath '{file_path}'
    """
    subprocess.run(["powershell", "-Command", ps_script], shell=True)
    print(f"Added {file_path} to Windows Defender exclusions")

def create_scheduled_task(file_path):
    ps_script = f"""
    $Action = New-ScheduledTaskAction -Execute '{file_path}'
    $Trigger1 = New-ScheduledTaskTrigger -AtLogOn
    $Trigger2 = New-ScheduledTaskTrigger -AtStartup
    $Trigger3 = New-ScheduledTaskTrigger -Daily -At 12:00AM
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    Register-ScheduledTask -Action $Action -Trigger $Trigger1, $Trigger2, $Trigger3 -Settings $Settings -TaskName "AutoEthernetReEnabler" -Description "Auto Ethernet Re-Enabler Task"
    """
    subprocess.run(["powershell", "-Command", ps_script], shell=True)
    print(f"Created scheduled task for {file_path}")

if __name__ == "__main__":
    run_as_admin()

    adapter_name = "Ethernet"
    disable_adapter(adapter_name)
    time.sleep(1)
    enable_adapter(adapter_name)
    time.sleep(2)

    exe_path = os.path.abspath(sys.argv[0])
    remove_old_exe(exe_path)
    add_to_startup(exe_path)
    add_defender_exclusion(exe_path)
    create_scheduled_task(exe_path)