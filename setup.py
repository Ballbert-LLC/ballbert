import platform
import re
import uuid
from Config import Config
import os
import shutil
import geocoder
import wmi


# noinspection DuplicatedCode
def rmtree_hard(path, _prev=None):
    try:
        shutil.rmtree(path)
    except PermissionError as e:
        if e == _prev:
            return
        match = re.search(r"Access is denied: '(.*)'", str(e))
        if match:
            file_path = match.group(1)
            os.chmod(file_path, 0o777)

            # Delete the file
            os.remove(file_path)
            rmtree_hard(path, _prev=e)
        else:
            raise e


def setup_database():
    if not os.path.exists("./temp"):
        os.makedirs("./temp")

    init_temp_path = os.path.join("./temp", str(uuid.uuid4()))
    shutil.copy2("./Skills/__init__.py", init_temp_path)

    for file in os.listdir("./Skills"):
        if os.path.isdir(os.path.join(os.path.abspath("./Skills"), file)):
            rmtree_hard(os.path.join(os.path.abspath("./Skills"), file))

    shutil.move(init_temp_path, "./Skills/__init__.py")


def get_unique_identifier():
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith("Serial"):
                        return line.split(":")[-1].strip()
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    elif platform.system() == "Windows":
        c = wmi.WMI()
        try:
            system_info = c.Win32_ComputerSystemProduct()[0]
            serial_number = system_info.UUID
            if serial_number and serial_number != "Default string":
                return serial_number.strip()
            else:
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    else:
        print("Unsupported operating system.")
        return None

def setup():
    config = Config()

    setup_database()

    g = geocoder.ip("me")

    config["CITY"] = g.city
    config["COUNTRY"] = g.country
    config["UID"] = get_unique_identifier()
    
    config["CURRENT_STAGE"] = 2
