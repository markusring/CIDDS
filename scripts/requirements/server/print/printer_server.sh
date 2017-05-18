#!/bin/bash

# Set system time 
rm /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Update the system
apt-get update
apt-get -y upgrade

# Define the packets to install with apt-get 
declare -a packagesAptGet=("cups-pdf" "samba")

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

apt-get -y update
apt-get -y upgrade

#Restart cups, otherwise /etc/cups/printers.conf dose not exist
service cups restart

#Share PDF Printer
sed -i "s/Shared No/Shared Yes/" /etc/cups/printers.conf

#Make printer available in Network
sed -i "s/Listen localhost:631/Listen *:631/" /etc/cups/cupsd.conf
sed -i "/<Location \/>/a \ \ Allow All" /etc/cups/cupsd.conf

# Cron daemon set up to make every night at 01:00 clock updates
echo -e "0 1 * * * sudo bash -c 'apt-get update && apt-get upgrade' >> /var/log/apt/myupdates.log\n" | crontab -

# Configure auto login 
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin debian --noclear %I 38400 linux
EOF

# Add user for ssh script 
useradd -m -s /bin/bash stack
echo "stack:YOUR_PASSWORD" | chpasswd
usermod -a -G sudo stack

# Prettify Prompt 
echo -e "PS1='\[\033[1;37m\]\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\[\033[41;37m\]\w\$\[\033[0m\] '" >> /home/debian/.bashrc

reboot
