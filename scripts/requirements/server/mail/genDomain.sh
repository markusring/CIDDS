#!/bin/bash

DBHOST=localhost
DBUSERNAME=root
DBUSERPASS=PWfMS2015
DBNAME=postfixdb

if [ -n "$1" ]; then
    echo "input ok"
else
    echo "Correct usage: sh script.sh domain"
    exit
fi

domain=$1
aliases=10
mailboxes=10
maxquota=10
quota=2048
transport=virtual
backupmx=0
active=1

mysql --host=$DHBOST --user=$DBUSERNAME --password=$DBUSERPASS postfixdb << EOF
insert into domain (domain,aliases,mailboxes,maxquota,quota,transport,backupmx,active) values('$domain','$aliases','$mailboxes','$maxquota','$quota','$transport','$backupmx','$active');
EOF
