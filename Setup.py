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

def prepare_parrent_dir(path):
    parrent_directory = os.path.abspath(os.path.join(path, os.pardir))
    if not os.path.exists(parrent_directory):
        logging.debug(f"Created directory for file {parrent_directory}.")
        os.mkdir(parrent_directory)


def create_temporary_directory(filename):
    dirpath = tempfile.mkdtemp()
    delimeter = {"Windows": "\\", "Darwin": "/", "Linux": "/"}.get(platform.system())
    logging.debug(f"Defined path delimeter for OS: {delimeter}.")
    path = delimeter.join([dirpath, filename])
    logging.debug(f"Created temporary directory and file: {path}.")
    return path


def prepare_place_for_download(path_to_download, url):
    if path_to_download is None:
        filename = url.split("/")[-1]
        path_to_download = create_temporary_directory(filename)
    elif isinstance(path_to_download, str):
        prepare_parrent_dir(path_to_download)
    return path_to_download


def download_file(url, progress_bar_description="", path_to_download=None):
    logging.debug(f"Got url with description: {url} / {progress_bar_description}.")
    path_to_download = prepare_place_for_download(path_to_download, url)
    logging.debug(f"Downloaded file will store here: {path_to_download}.")
    with requests.get(url, stream=True) as r:
        total = int(r.headers.get("content-length", 0))
        logging.debug(f"Downloaded file will take next disk storage: {total} bytes.")
        block_size = 2048
        with open(path_to_download, "wb") as f, tqdm(
            desc=progress_bar_description, total=total, unit="B", unit_scale=True
        ) as bar:
            for data in r.iter_content(block_size):
                bar.update(len(data))
                f.write(data)
    logging.debug(f"Downloading complete. File save to {path_to_download}.")
    return path_to_download


def is_installed_python(version):
    for python in ["python", "python3"]:
        try:
            process = subprocess.Popen(
                [python, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            continue
        stdout, stderr = process.communicate()
        if version in str(stdout):
            return True
    return False

def is_installed_touchdesigner(version):
    try:
        process = subprocess.Popen(
            ["touchdesiger", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if version in str(stdout):
            return True
        return False
    except FileNotFoundError:
        return False

def install_python(version):
    if is_installed_python(version):
        logging.debug(f"Python {version} already installed.")
        return
    logging.debug(f"Staring to install python{version}..")
    if architecture == "64bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe",
            "Downloading python3",
        )
    elif architecture == "32bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}.exe",
            "Downloading python3",
        )
    else:
        raise Exception(f"Undefiend architecture: {platform.architecture()}")

    logging.debug(f"Downloading complete.")
    logging.debug(f"Starting installing..")
    process = subprocess.Popen(
        [
            python_exe_path,
            "/quiet",
            "PrependPath=1",
            "Include_test=0",
            "CompileAll=1",
            "Include_tcltk=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.debug(f"Installing python{version} complete.")


def install_dependencies(path_pip="C:\\Program Files (x86)\\EVR\\requirements.txt"): 
    logging.debug(f"Staring to install python requirements from path: {path_pip} ..")
    
    process = subprocess.Popen(
        ["python", "-m","pip", "install", "-r", path_pip],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = process.communicate()
    logging.debug(f"Complete installing python requirements.")


def install_touchdesigner(version):
    if is_installed_touchdesigner(version):
        logging.debug(f"TouchDesigner {version} already installed.")
        return
    touchdesiger_exe_path = download_file(
        f"https://download.derivative.ca/TouchDesigner.{version}.exe",
        "Downloading TouchDesigner",
    )
    logging.debug(f"Staring to install TouchDesigner..")
    process = subprocess.Popen(
        [touchdesiger_exe_path, "/VERYSILENT"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.debug(f"Complete installing TouchDesigner.")

def install_ndi_tools():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.by/d/5qylbuELKWb98A'  

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    ndi_tools_exe_path = download_file(download_url)
    os.rename(ndi_tools_exe_path,f"{ndi_tools_exe_path}.exe")
    logging.debug(f"Staring to install ndi_tools...........")
    process = subprocess.Popen(
        [f'{ndi_tools_exe_path}.exe', 
        "/VERYSILENT", 
        "/NORESTART", 
        "/TYPE=all_tools", 
        "/SP-",
        ],

        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.debug(f"Complete installing ndi_Tols.")


def obs_ndi():
    obs_dni_exe_path = download_file(
        f"https://github.com/Palakis/obs-ndi/releases/download/4.9.1/obs-ndi-4.9.0-Windows-Installer.exe",
        "Downloading Obs_dni",
    )
    logging.debug(f"Staring to OBs ndi..")
    process = subprocess.Popen(
        [  obs_dni_exe_path, "/VERYSILENT"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = process.communicate()
    logging.debug(f"Complete installing OBs_ndi.")

def download_media_files():
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.by/d/2Q1R9kcYKl9Q-Q'  

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    zip_path = download_file(download_url)
    os.rename(zip_path, f'{zip_path}.zip')
    fantasy_zip = zipfile.ZipFile(f'{zip_path}.zip')
    fantasy_zip.extractall('C:\\Program Files (x86)\\EVR\\')#Указать место
    fantasy_zip.close()

def download_project_toe():
    directory = 'C:\\Program Files (x86)\\EVR\\'
    base_url = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
    public_key = 'https://disk.yandex.by/d/fngADNHpJVLcuA'

    final_url = base_url + urlencode(dict(public_key=public_key))
    response = requests.get(final_url)
    download_url = response.json()['href']
    project_path = download_file(download_url)
    rename = os.rename(project_path, f'{project_path}.toe')
    shutil.move(f'{project_path}.toe', f'{directory}Project.toe')
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting to install tools..")

    architecture = platform.architecture()[0]
    logging.debug(f"Defined next architecture: {architecture}.")

    install_python(version="3.9.6")
    install_touchdesigner(version="2021.14360")
    install_ndi_tools()
    obs_ndi()
    download_media_files()
    install_dependencies()
    download_project_toe()
