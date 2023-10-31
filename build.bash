sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev --fix-missing
sudo apt install -y python3-pyaudio
sudo apt-get install -y python3-dev libasound2-dev
sudo pip3 install simpleaudio
sudo pip3 install PyAudio
sudo apt-get install -y libffi6 libffi-dev
sudo pip3 install cython
sudo pip3 install numpy
sudo pip3 install manimlib
sudo pip3 install soxr
sudo pip3 install google-cloud-speech
sudo pip3 install google-cloud-texttospeech
sudo apt-get install flac
sudo chmod 744 ./start.sh
sudo pip3 install -r requirements.txt
sudo mkdir -p /etc/ballbert
sudo touch /etc/ballbert/logs.txt
sudo touch /opt/ballbert/logs.txt


# Path to the autostart file
autostart_file="/etc/xdg/lxsession/LXDE-pi/autostart"

echo "@sudo /opt/ballbert/start.sh" | sudo tee "$autostart_file" > /dev/null

sudo raspi-config nonint do_wifi_country US
sudo connmanctl enable wifi
sudo rfkill unblock wifi

sudo python3 /opt/ballbert/ap_mode.py
