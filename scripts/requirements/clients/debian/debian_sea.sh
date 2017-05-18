#!/bin/bash

# Set system time 
rm /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Add to start
crontab -r

# Download the scripts from the webserver 
wget YOUR_SERVER_IP/scripts/automation.zip

# Add sources  
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 8756C4F765C9AC3CB6B85D62379CE192D401AB61
echo deb http://dl.bintray.com/seafile-org/deb jessie main | sudo tee /etc/apt/sources.list.d/seafile.list

### Prepare the clients for the automation 

# Update the system 
apt-get -y update
apt-get -y upgrade

# Define the packets to install with apt-get 
declare -a packagesAptGet=("aptitude" "python" "python-xlib" "python-cups" "python-pip" "iceweasel" "xvfb" "unzip" "cups" "cups-client" "cups-bsd" "cifs-utils" "cmake" "sqlite3" "python2.7" "python-setuptools" "python-simplejson" "python-imaging" "autoconf" "automake" "libtool" "libevent-dev" "libcurl4-openssl-dev" "libgtk2.0-dev" "uuid-dev" "intltool" "libsqlite3-dev" "valac" "libjansson-dev" "libqt4-dev" "libfuse-dev" "seafile-cli" "grub2" "nmap") 

# Install all predefined packages 
for package in "${packagesAptGet[@]}"
do
	echo "Looking for package $package."
	until dpkg -s $package | grep -q Status;
	do
	    echo "$package not found. Installing..."
	    apt-get --force-yes --yes install $package
	done
	echo "$package found."
done

# Definition of the Python-Libraries to install 
declare -a packagesPip=("selenium" "pyvirtualdisplay" "xvfbwrapper" "pexpect" "python-nmap")

# Install Python-Libs using pip 
for package in "${packagesPip[@]}"
do
	echo "Looking for package $package."
	until pip show $package | grep -q Location;
	do
		echo "$package not found. Installing..."
		pip install $package
	done
	echo "$package found."
done

# Update the system 
aptitude -y update
aptitude -y upgrade

# Install the geckodriver for selenium (needed for browsing)
wget "https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz"
tar -xzf "geckodriver-v0.11.1-linux64.tar.gz"
mv geckodriver /opt/

# Configure printers 
/etc/init.d/cups restart
lpoptions -d pdf
/etc/init.d/cups restart

# Create directory for Netstorage 
mkdir -pv /home/debian/netstorage

# Create directory for local storage 
mkdir -pv /home/debian/localstorage

# Create directory for log files  
mkdir -pv /home/debian/log

# Configure Seafile (Cloud storage)
mkdir -pv /home/debian/sea /home/debian/seafile-client
seaf-cli init -d /home/debian/seafile-client -c /home/debian/.ccnet
seaf-cli start -c /home/debian/.ccnet
seaf-cli config -k disable_verify_certificate -v true -c /home/debian/.ccnet
seaf-cli config -k enable_http_sync -v true -c /home/debian/.ccnet
seaf-cli stop -c /home/debian/.ccnet
seaf-cli start -c /home/debian/.ccnet
chown -R debian:debian /home/debian/sea/ /home/debian/seafile-client/ /home/debian/.ccnet
echo -e "@reboot sleep 60 && seaf-cli start -c /home/debian/.ccnet 2>&1 > /dev/null\n" | crontab -

# Generate dummy files for seafile
mkdir -pv /home/debian/tmpseafiles
i=0
while [ $i -le 100 ]
do
  i=`expr $i + 1`;
  zufall=$RANDOM;
  zufall=$(($zufall % 9999))
  dd if=/dev/zero of=/home/debian/tmpseafiles/test-`expr $zufall`.dat bs=1K count=`expr $zufall`
done

chown -R debian:debian /home/debian/tmpseafiles/
chmod -R 755 /home/debian/tmpseafiles/ 
chmod -R 755 /home/debian/sea

# Unzip the downloaded scripts from Server 
unzip automation.zip -d /home/debian/
chmod -R 755 /home/debian/automation
chown -R debian:debian /home/debian/automation

# Configure auto login after booting the OS 
mkdir -pv /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin debian --noclear %I 38400 linux
EOF

# Set up services for scripts 
cat > /etc/systemd/system/automation.service <<EOF
[Unit]
Description=Start automation scripts

[Service]
WorkingDirectory=/home/debian/automation/
ExecStart=/usr/bin/python readIni.py
Type=simple

[Install]
WantedBy=multi-user.target
EOF

# Reload Systemd manager  
systemctl daemon-reload

# Activate services
systemctl enable automation.service

# Prettify Prompt 
echo -e "PS1='\[\033[1;37m\]\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\[\033[41;37m\]\w\$\[\033[0m\] '" >> /home/debian/.bashrc

# Restart 
reboot
