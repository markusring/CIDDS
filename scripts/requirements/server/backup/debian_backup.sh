#!/bin/bash

# Set system time 
rm /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# Update the system
apt-get -y update
apt-get -y upgrade

# Define the packets to install with apt-get 
declare -a packagesAptGet=("samba")

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

# Update the system
apt-get -y update
apt-get -y upgrade

# Create directories for samba 
mkdir /media/webserverbackup
mkdir /media/fileserverbackup
mkdir /media/mailserverbackup

# Change the permissions on these folders 
chmod 777 /media/webserverbackup
chmod 777 /media/fileserverbackup
chmod 777 /media/mailserverbackup

# Delete the folders regularly to save memory 
echo -e "0 20 * * * sudo bash -c 'rm -r /media/webserverbackup/*'" >> mycron
echo -e "0 20 * * * sudo bash -c 'rm -r /media/fileserverbackup/*'" >> mycron
echo -e "0 20 * * * sudo bash -c 'rm -r /media/mailserverbackup/*'" >> mycron

# Create Cron-Daemon which deletes every night at 01:00 the backup folders 
echo -e "0 1 * * * sudo bash -c 'apt-get update && apt-get upgrade' >> /var/log/apt/myupdates.log\n" >> mycron

crontab mycron
rm mycron

# Create samba configuration 
# create mask und force create mode (necessary for overwriting files in the Inbox)
cat > /etc/samba/smb.conf <<EOF
[global]
workgroup = WORKGROUP
security = user
map to guest = bad user

[backup_webserver]
comment = Backup for webserver 
path = /media/webserverbackup
read only = no
guest ok = yes
create mask = 777
force create mode = 777

[backup_fileserver]
comment = Backup for Fileserver
path = /media/fileserverbackup
read only = no
guest ok = yes
create mask = 777
force create mode = 777

[backup_mailserver]
comment = Backup for Mailserver
path = /media/mailserverbackup
read only = no
guest ok = yes
create mask = 777
force create mode = 777
EOF

# Create auto login 
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin debian --noclear %I 38400 linux
EOF

# Prettify Prompt 
echo -e "PS1='\[\033[1;37m\]\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\[\033[41;37m\]\w\$\[\033[0m\] '" >> /home/debian/.bashrc

# Reboot
reboot
