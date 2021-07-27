@ECHO OFF

rem for build use pyinstaller version >= 4.3
pip install -r .\requirements.txt --cache-dir .\pypackages
pyinstaller.exe --noconfirm --log-level ERROR ^
                --onefile --uac-admin ^
                --clean --name Installer-CON-X ^
                --paths .\pypackages .\setup.py

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

echo "Installer store in `setup` directory"
timeout 30
