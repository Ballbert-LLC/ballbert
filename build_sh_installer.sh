wget https://raw.githubusercontent.com/Ballbert-LLC/ballbert/master/build.sh
sudo chmod 744 ./build.sh
#Autostart
autostart_file="/etc/xdg/lxsession/LXDE-pi/autostart"

echo "@sudo $PWD/build.sh" | sudo tee "$autostart_file" > /dev/null