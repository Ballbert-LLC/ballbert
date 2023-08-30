import os
from Config import Config

config = Config()


def disable_access_point():
    os.system("systemctl disable dnsmasq")
    os.system("systemctl disable hostapd")

    os.system("sudo cp /etc/dnsmasq.conf.copy /etc/dnsmasq.conf")
    os.system("sudo cp /etc/dhcpcd.conf.copy /etc/dhcpcd.conf")

    config["CURRENT_STAGE"] = 1

    os.system("reboot")
