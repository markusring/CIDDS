#ps1

# Create a windows user which is automatically logged on to the system 
New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name AutoAdminLogon -Value 1
New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name DefaultUserName -Value "winuser"
New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -Name DefaultPassword -Value winuser

# Create folder for the automation scripts 
new-item C:\skripte -ItemType directory

# Download the scripts 
python -c "import urllib2; f = open('C:/skripte/automation.zip', 'wb+'); f.write(urllib2.urlopen('YOUR_SERVER_IP/scripts/automation.zip').read());"
python -c "import zipfile; z = zipfile.ZipFile('C:/skripte/automation.zip'); z.extractall('C:/skripte');"

# Create a subfolder that maintains the dependencies for the Windows system
new-item C:\skripte\requirements -ItemType directory

# Set time zone 
tzutil /s "Central Europe Standard Time"

# Syncronize the system with the internet 
net start w32time
w32tm /resync /force

# pywin (Access to the Windows-API)
python -c "import urllib2; f = open('C:/skripte/requirements/pywin32.zip', 'wb+'); f.write(urllib2.urlopen('https://pypi.python.org/packages/91/87/2ed2b036a2dd9037074ba5862ff959e9541b9625f3ae8c90b8bacd38589b/pypiwin32-219.win32-py2.7.exe#md5=bb89d94a26197a467b27f9de2b24a344').read());"
python -c "import zipfile; z = zipfile.ZipFile('C:/skripte/requirements/pywin32.zip'); z.extractall('C:/skripte/requirements');"

# install pywin
xcopy C:\skripte\requirements\PLATLIB\* C:\Python27\Lib\site-packages\ /s /e /y
xcopy C:\skripte\requirements\SCRIPTS\* C:\Python27\Lib\site-packages\ /s /e /y
cd C:\Python27\Lib\site-packages\
python pywin32_postinstall.py -install
rm pywin32_postinstall.py

# Insert the automation scripts in autostart of windows 
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("C:\Users\winuser\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Mainscript.lnk")
$Shortcut.TargetPath = "C:\skripte\automation\readIni.py"
$Shortcut.WorkingDirectory = "C:\skripte\automation\"
$Shortcut.Save()

# Create a folder for storing files from the NetStorage
new-item C:\localstorage\ -ItemType directory

# Prevent updates for Firefox --> Updates lead to possible problems with Selenium 
$profileFolder = get-childitem -path "C:\Users\winuser\AppData\Roaming\Mozilla\Firefox\Profiles" | select-object -last 1 fullname | split-path -noqualifier
$profileFolder = $("C:" + $profileFolder.substring(0, $profileFolder.length-1) + "\")
$userFile = $($profileFolder + "prefs.js")
'user_pref("app.update.auto", false);user_pref("app.update.enabled", false);' | add-content $userFile

exit 1001
