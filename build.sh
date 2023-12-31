#Settings - Screen Sleep
sudo xset -dpms

#Install
sudo git clone https://github.com/Ballbert-LLC/ballbert.git /opt/ballbert

cd /opt/ballbert
#Autostart
autostart_file="/etc/xdg/lxsession/LXDE-pi/autostart"

echo "@xscreensaver -no-splash
@sudo /opt/ballbert/start.sh
@xset s off
@xset -dpms
@feh --bg-fill /opt/ballbert/assets/ballbert_background.png" | sudo tee "$autostart_file" > /dev/null

#Wifi
sudo raspi-config nonint do_wifi_country US
sudo connmanctl enable wifi
sudo rfkill unblock wifi

#Logging
sudo touch /opt/ballbert/console_logs.txt
sudo touch /opt/ballbert/logs.log

#Requirements - Desktop
sudo apt-get install feh -y

#Requirements - Audio
sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev --fix-missing
sudo apt install -y python3-pyaudio
sudo apt-get install -y python3-dev libasound2-dev
sudo pip3 install simpleaudio
sudo pip3 install PyAudioF
sudo apt-get install -y libffi6 libffi-dev
sudo pip3 install --no-cache-dir SpeechRecognition==3.10.0

#Requirements - requirements.txt
python3 -m pip3 cache purge
sudo pip3 install --no-cache-dir -r /opt/ballbert/requirements.txt

#Permissions
sudo chmod 744 /opt/ballbert/start.sh

#Kickstart program via calling ap mode which will put the device in access point mode and then restart which will trigger the autostart program.
sudo python3 /opt/ballbert/ap_mode.py
