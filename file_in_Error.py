import logging
import platform
import shutil
import subprocess
import tempfile
import os

import requests
from tqdm import tqdm
from urllib.parse import urlencode
import zipfile 

obs_dni_exe_path = 'F:\\Work\\TZ\\testzip\\obs-ndi-4.9.0-Windows.zip'

fantasy_zip = zipfile.ZipFile(obs_dni_exe_path)# путь к архиву
fantasy_zip.extractall('F:\\Work\\TZ\\testzip\\')
fantasy_zip.close()
os.chmod ( "F:\\Work\\TZ\\testzip\\obs-plugins\\64bit\\obs-ndi.dll", 0o775) 
os.remove('F:\\Work\\TZ\\testzip\\obs-plugins\\64bit\\obs-ndi.dll', dir_fd='F:\\проги\\OBS\\obs-studio\\obs-plugins\\64bit')
os.chmod ( "F:\\Work\\TZ\\testzip\\obs-plugins\\64bit\\obs-ndi.pdb", 0o775) 
os.remuve('F:\\Work\\TZ\\testzip\\obs-plugins\\64bit\\obs-ndi.pdb', dir_fd='F:\\проги\\OBS\\obs-studio\\obs-plugins\\64bit')
os.chmod ( "F:\\Work\\TZ\\testzip\\data\\obs-plugins\\obs-ndi", 0o775) 
os.remove('F:\\Work\\TZ\\testzip\\data\\obs-plugins\\obs-ndi', dir_fd='F:\\проги\\OBS\\obs-studio\\data\\obs-plugins')
os.remove(path, dir_fd=...)

# F:\проги\OBS\obs-studio\obs-plugins\64bit
# F:\проги\OBS\obs-studio\data\obs-plugins