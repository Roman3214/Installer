import hashlib
import logging
import os
import platform
import shutil
import subprocess
import tempfile

import requests
import winapps
from tqdm import tqdm

from ascii_logo import hello_page


def prepare_parrent_dir(path):
    parrent_directory = os.path.abspath(os.path.join(path, os.pardir))
    if not os.path.exists(parrent_directory):
        logging.debug(f"Created directory for file {parrent_directory}.")
        os.mkdir(parrent_directory)


def create_temporary_directory(filename):
    unique_directory_identificator = "evr_"
    dirpath = (
        unique_directory_identificator + hashlib.md5(filename.encode()).hexdigest()
    )
    path = delimeter.join([tempfile.gettempdir(), dirpath, filename])
    logging.debug(f"Created temporary directory and file: {path}.")
    return path


def prepare_place_for_download(path_to_download, url):
    if path_to_download is None:
        filename = hashlib.md5(url.encode()).hexdigest()
        path_to_download = create_temporary_directory(filename)
    prepare_parrent_dir(path_to_download)
    return path_to_download


def is_already_downloaded(path_to_download, url):
    if not os.path.exists(path_to_download):
        return False

    file_size = requests.head(url, allow_redirects=True).headers.get(
        "content-length", 0
    )
    file_size = int(file_size)
    if file_size > 0 and os.path.getsize(path_to_download) == file_size:
        return True
    return False


def get_first_file_bytes(url):
    binary_content = b""
    if requests.head(url).headers.get("Accept-Ranges"):
        binary_content = requests.get(url, headers={"Range": "bytes=0-1"}).content
    else:
        with requests.get(url, stream=True) as req:
            block_size = 2
            for data in req.iter_content(block_size):
                binary_content = data
                break

    return binary_content.hex().lower()


def define_extension(url):
    known_extensions = {
        "377a": ".7z",
        "4d5a": ".exe",
        "504b": ".zip",
        "5261": ".rar",
        "3130": ".toe",
    }

    header_magic_number = get_first_file_bytes(url)

    extension = known_extensions.get(header_magic_number, ".UNKNOWN")
    logging.debug(f"Defined extension for remote file: {url} is {extension}.")
    return extension


def download_file(
    url,
    progress_bar_description="",
    path_to_download=None,
    _application_log_name="",
    **kwargs,
):
    logging.debug(f"Got url {url} with description: {progress_bar_description}.")
    logging.info(f"Starting download {_application_log_name}..")

    if kwargs.get("original_url"):
        path_to_download = prepare_place_for_download(
            path_to_download, kwargs["original_url"]
        )
    else:
        path_to_download = prepare_place_for_download(path_to_download, url)

    path_to_download = path_to_download + define_extension(url)

    if is_already_downloaded(path_to_download, url):
        logging.info(f"{_application_log_name} already downloaded.")
        return path_to_download

    logging.debug(f"Downloaded file will store here: {path_to_download}.")
    with requests.get(url, stream=True) as r:
        total = int(r.headers.get("content-length", 0))
        logging.debug(f"Downloaded file will take next disk storage: {total} bytes.")
        block_size = 2048
        with open(path_to_download, "wb") as file, tqdm(
            desc=progress_bar_description,
            total=total,
            unit="B",
            unit_scale=True,
            ascii=True,
        ) as progress_bar:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
    logging.debug(f"Downloading complete. File save to {path_to_download}.")
    logging.info(f"Downloading complete {_application_log_name}.")
    return path_to_download


def is_installed_python(version):
    for python in ["python", "python3"]:
        try:
            process = subprocess.Popen(
                [python, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            continue
        stdout, _ = process.communicate()
        if version in str(stdout):
            return True
    return False


def is_exists_path(path):
    return os.path.exists(path)


def is_installed_application(name):
    try:
        if next(winapps.search_installed(name)):
            return True
    except StopIteration:
        return False
    return False


def execute_command(command, is_need_split=True, _application_log_name=""):
    logging.debug(f"Got command for execute: {command}")
    logging.info(f"Starting installation {_application_log_name}..")
    if is_need_split:
        command = command.split(" ")
    logging.debug(f"Got command for execute: {command}")
    subprocess.Popen(command, shell=True).wait()
    logging.info(f"Installing {_application_log_name} complete.")


def install_obs_studio(version):
    _application_log_name = f"OBS Studio {version}"

    if is_installed_application("OBS Studio"):
        logging.info(f"{_application_log_name} already installed.")
        return

    if architecture == "64bit":
        obs_exe_path = download_file(
            f"https://github.com/obsproject/obs-studio/releases/download/{version}/OBS-Studio-{version}-Full-Installer-x64.exe",
            "Downloading obs",
            _application_log_name=_application_log_name,
        )
    elif architecture == "32bit":
        obs_exe_path = download_file(
            f"https://github.com/obsproject/obs-studio/releases/download/{version}/OBS-Studio-{version}-Full-Installer-x86.exe",
            "Downloading obs",
            _application_log_name=_application_log_name,
        )
    else:
        raise Exception(f"Undefiend architecture: {platform.architecture()}")

    execute_command(f"{obs_exe_path} /S", _application_log_name)


def install_python(version):
    _application_log_name = f"Python {version}"
    if is_installed_python(version):
        logging.info(f"{_application_log_name} already installed.")
        return
    if architecture == "64bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}-amd64.exe",
            "Downloading python3",
            _application_log_name=_application_log_name,
        )
    elif architecture == "32bit":
        python_exe_path = download_file(
            f"https://www.python.org/ftp/python/{version}/python-{version}.exe",
            "Downloading python3",
            _application_log_name=_application_log_name,
        )
    else:
        raise Exception(f"Undefiend architecture: {platform.architecture()}")

    execute_command(
        f"{python_exe_path} /quiet PrependPath=1 Include_test=0 CompileAll=1 Include_tcltk=0",
        _application_log_name,
    )


def install_dependencies(path_pip):
    logging.info(f"Starting installation python requirements from path: {path_pip} ..")
    execute_command(
        ["python", "-m", "pip", "install", "-r", f"{path_pip}"], is_need_split=False
    )
    logging.info("Completed installation python requirements.")


def install_touchdesigner(version):
    _application_log_name = f"TouchDesigner {version}"
    for default_touchdesiger_exe_path in winapps.search_installed("TouchDesigner"):
        if default_touchdesiger_exe_path:
            logging.info(f"{_application_log_name} already installed.")
            return

    touchdesiger_exe_path = download_file(
        f"https://download.derivative.ca/TouchDesigner.{version}.exe",
        "Downloading TouchDesigner",
        _application_log_name=_application_log_name,
    )

    execute_command(f"{touchdesiger_exe_path} /VERYSILENT", _application_log_name)


def download_file_from_yandex_disk(
    url, progress_bar_description="", path_to_download=None, _application_log_name=""
):
    base_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"

    response = requests.get(base_url, params={"public_key": url})
    download_url = response.json().get("href")
    return download_file(
        download_url,
        progress_bar_description,
        path_to_download,
        _application_log_name,
        original_url=url,
    )


def install_ndi_tools(yandex_disk_url):
    _application_log_name = "NDI Tools"
    if is_installed_application("NDI 4 Tools"):
        logging.info(f"{_application_log_name} already installed.")
        return

    ndi_tools_exe_path = download_file_from_yandex_disk(
        yandex_disk_url,
        "Downloading NDI Tools",
        _application_log_name=_application_log_name,
    )

    execute_command(
        f"{ndi_tools_exe_path} /VERYSILENT /NORESTART /TYPE=all_tools /SP-",
        _application_log_name,
    )


def install_obs_ndi(url):
    _application_log_name = "OBS NDI"
    if not is_installed_application("OBS Studio"):
        logging.warning("OBS Studio not installed.")
        logging.warning("OBS NDI not installed.")
        return

    if is_installed_application("obs-ndi"):
        logging.info(f"{_application_log_name} already installed.")
        return

    obs_ndi_exe_path = download_file(
        url, "Downloading OBS NDI", _application_log_name=_application_log_name
    )

    execute_command(
        f"{obs_ndi_exe_path} /VERYSILENT /COMPONENTS=''", _application_log_name
    )


def download_media_files(yandex_disk_url):
    _application_log_name = "media files"
    if is_exists_path(delimeter.join([default_path, "AUTO_CONF_LOCATIONS"])):
        logging.info(f"{_application_log_name} already exists.")
        return

    media_files = download_file_from_yandex_disk(
        yandex_disk_url,
        "Downloading media files",
        _application_log_name=_application_log_name,
    )

    shutil.unpack_archive(media_files, default_path)
    logging.info("Completed extract media files.")


def download_project_toe(yandex_disk_url):
    _application_log_name = "TouchDesigner project"
    path_to_download = delimeter.join([default_path, "Awesome-Project"])

    if is_exists_path(path_to_download):
        logging.info(f"{_application_log_name} already exists.")
        return

    download_file_from_yandex_disk(
        yandex_disk_url,
        "Downloading TouchDesigner projects",
        path_to_download,
        _application_log_name=_application_log_name,
    )


def cleanup():
    logging.info("Starting cleanup %TEMP% directory..")
    for directory in os.listdir(tempfile.gettempdir()):
        if directory.startswith("evr_"):
            path = delimeter.join([tempfile.gettempdir(), directory])
            logging.debug(f"Starting delete directory: {path}")
            shutil.rmtree(path)
    logging.info("Completed cleanup %TEMP% directory.")


if __name__ == "__main__":
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper().strip()
    logging.basicConfig(
        level=LOGLEVEL,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d/%m %I:%M:%S",
    )

    hello_page()

    logging.debug("Starting installation tools..")

    architecture = platform.architecture()[0]
    logging.debug(f"Defined next architecture: {architecture}.")

    default_path = "C:\\Program Files (x86)\\CON-X"
    logging.debug(f"Defined default extract path: {default_path}.")

    delimeter = {"Windows": "\\", "Darwin": "/", "Linux": "/"}.get(platform.system())
    logging.debug(f"Defined path delimeter for OS: {delimeter}.")

    install_obs_studio(version="27.0.1")
    install_python(version="3.9.6")
    install_touchdesigner(version="2021.14360")
    install_ndi_tools("https://disk.yandex.by/d/5qylbuELKWb98A")
    install_obs_ndi(
        "https://github.com/Palakis/obs-ndi/releases/download/4.9.1/obs-ndi-4.9.0-Windows-Installer.exe"
    )
    download_media_files("https://disk.yandex.by/d/2Q1R9kcYKl9Q-Q")
    install_dependencies(delimeter.join([default_path, "requirements.txt"]))
    download_project_toe("https://disk.yandex.by/d/fngADNHpJVLcuA")

    cleanup()
