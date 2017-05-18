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

# Create directory which should be released 
mkdir /media/storage

# Create dummy files 
dd if=/dev/zero of=/media/storage/file30kB.dat bs=1K count=30
dd if=/dev/zero of=/media/storage/file40kB.dat bs=1K count=40
dd if=/dev/zero of=/media/storage/file50kB.dat bs=1K count=50
dd if=/dev/zero of=/media/storage/file100kB.dat bs=1K count=100
dd if=/dev/zero of=/media/storage/file500kB.dat bs=1K count=500
dd if=/dev/zero of=/media/storage/file1MB.dat bs=1M count=1
dd if=/dev/zero of=/media/storage/file2MB.dat bs=1M count=2
dd if=/dev/zero of=/media/storage/file3MB.dat bs=1M count=3
dd if=/dev/zero of=/media/storage/file4MB.dat bs=1M count=4
dd if=/dev/zero of=/media/storage/file5MB.dat bs=1M count=5
dd if=/dev/zero of=/media/storage/file6MB.dat bs=1M count=6
dd if=/dev/zero of=/media/storage/file7MB.dat bs=1M count=7
dd if=/dev/zero of=/media/storage/file8MB.dat bs=1M count=8
dd if=/dev/zero of=/media/storage/file9MB.dat bs=1M count=9
dd if=/dev/zero of=/media/storage/file10MB.dat bs=1M count=10
dd if=/dev/zero of=/media/storage/file50MB.dat bs=1M count=50
dd if=/dev/zero of=/media/storage/file100MB.dat bs=1M count=100
dd if=/dev/zero of=/media/storage/file300MB.dat bs=1M count=300
dd if=/dev/zero of=/media/storage/file700MB.dat bs=1M count=700

# Directory in which files can be copied
# The Inbox is necessary to avoid race conditions when writing to Netstorage
mkdir /media/storage/inbox

# Modify permissions so that files can be written
chmod 777 /media/storage/inbox

# Create Samba configuration 
# create mask und force create mode (necessary for overwriting files in the Inbox)
cat > /etc/samba/smb.conf <<EOF
[global]
workgroup = WORKGROUP
security = user
map to guest = bad user

[netstorage]
comment = Netstorage fuer OpenStack-VMs
path = /media/storage
read only = no
guest ok = yes
create mask = 777
force create mode = 777
EOF

# Configure auto login 
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin debian --noclear %I 38400 linux
EOF

# Mount the mount point for backup
mkdir /home/debian/backup/

# Download the script to set up the backup server
wget -O /home/debian/backup.py "YOUR_SERVER_IP/scripts/requirements/server/file/backup.py"

# Run the script to set up the backup server on a regular time interval 
echo -e "55 21 * * * sudo bash -c 'python /home/debian/backup.py'" >> mycron

# Run backup service periodically
echo -e "0 22 * * * sudo bash -c 'tar -cf /home/debian/backup/backup.tar /media/storage/'" >> mycron

# Cron daemon set up every night at 12:00 clock to delete all files from the inbox 
echo -e "0 0 * * * rm -r /media/storage/inbox/* >> /dev/null 2>&1" >> mycron

# Cron daemon set up to make every night at 01:00 clock updates
echo -e "0 1 * * * sudo bash -c 'apt-get update && apt-get upgrade' >> /var/log/apt/myupdates.log\n" >> mycron

crontab mycron
rm mycron

# Prepare for ssh user login (create stack user with appropriate password)
useradd -m -s /bin/bash stack
echo "stack:YOUR_PASSWORD" | chpasswd
usermod -a -G sudo stack

# Prettify Prompt
echo -e "PS1='\[\033[1;37m\]\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\[\033[41;37m\]\w\$\[\033[0m\] '" >> /home/debian/.bashrc

# Restart 
reboot
