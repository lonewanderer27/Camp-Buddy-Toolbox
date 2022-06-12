import platform
import subprocess
import os
import sys
import ntpath
import webbrowser
from rpatool.rpatool import RenPyArchive
import PySimpleGUI as sg
from pprint import pprint
from datetime import date

def center(elements):
    return [sg.Push(), *elements, sg.Push()]

def open_url(url):
    webbrowser.open(url)

def open_folder(path: str):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    else:
        return filename

todays_date = date.today()

def print_debug_info(window, event, values):
    print(f'\n\n{window} Event:\n')
    pprint(event, indent=2)
    print(f'\n\n{window} Values:\n')
    pprint(values, indent=2)
    print('')

def get_filename_from_path(rpapath: str) -> str:
    return ntpath.basename(rpapath)

def valid_path(rpapath: str):
    if not len(rpapath) == 0:
        return True
    else:
        return False

def valid_rpa_file(rpafile: str) -> tuple:
    rpaprocessor = RenPyArchive()
    try:
        rpaprocessor.load(filename=rpafile)
    except OSError as e:
        return False, "Error. File does not exist or permission denied"
    except ValueError as e:
        return False, "Error. Invalid archive"
    else:
        return True, f"Loading {get_filename_from_path(rpafile)}"

def list_rpa_files(rpafile: str) -> list:
    rpaprocessor = RenPyArchive(rpafile)
    files_list = sorted(rpaprocessor.list())
    return files_list