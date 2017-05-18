#!/bin/bash
rm /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Berlin /etc/localtime

mkdir /tmp/mailsetup
cd /tmp/mailsetup
wget YOUR_SERVER_IP/scripts/requirements/server/mail/mailserver.sh
wget YOUR_SERVER_IP/scripts/requirements/server/mail/genDomain.sh -O /tmp/mailsetup/genDomain.sh
wget YOUR_SERVER_IP/scripts/requirements/server/mail/genUser.sh -O /tmp/mailsetup/genUser.sh
source mailserver.sh
