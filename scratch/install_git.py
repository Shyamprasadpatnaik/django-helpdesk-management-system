import os
import urllib.request
import zipfile
import shutil

dest = os.path.expandvars(r'%LOCALAPPDATA%\Programs\Git')
zip_file = os.path.expandvars(r'%TEMP%\mingit.zip')
url = 'https://github.com/git-for-windows/git/releases/download/v2.55.0.windows.5/MinGit-2.55.0.5-64-bit.zip'

print(f'Downloading MinGit from {url}...')
urllib.request.urlretrieve(url, zip_file)
print(f'Extracting to {dest}...')
os.makedirs(dest, exist_ok=True)
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(dest)

if os.path.exists(zip_file):
    os.remove(zip_file)

cmd_path = os.path.join(dest, 'cmd')
git_exe = os.path.join(cmd_path, 'git.exe')

if os.path.exists(git_exe):
    print(f'Git successfully installed at: {git_exe}')
    # Add to User PATH
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Environment', 0, winreg.KEY_ALL_ACCESS)
    try:
        current_path, _ = winreg.QueryValueEx(key, 'Path')
    except FileNotFoundError:
        current_path = ''
    if cmd_path.lower() not in current_path.lower():
        new_path = current_path + ';' + cmd_path if current_path else cmd_path
        winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
        print('Added Git to User PATH in registry.')
    winreg.CloseKey(key)
else:
    print('Error: git.exe not found after extraction.')
