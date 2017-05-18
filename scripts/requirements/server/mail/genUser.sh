#!/bin/bash

DBHOST=localhost
DBUSERNAME=root
DBUSERPASS=PWfMS2015
DBNAME=postfixdb

if [ -n "$2" ]; then
    echo "input ok"
else
	echo "Correct usage: sh script.sh username domain"
    exit
fi

username=$1@$2
password=\$1\$f258886e\$mthkVuLZBDNEfnDbH3Gg51
maildir=$2/$1/
quota=0
local_part=$1
domain=$2


mysql --host=$DHBOST --user=$DBUSERNAME --password=$DBUSERPASS postfixdb << EOF
insert into mailbox (username,password,maildir,quota,local_part,domain) values('$username','$password','$maildir','$quota','$local_part','$domain');
EOF

address=$1@$2
goto=$1@$2
domain=$2
active=1

mysql --host=$DHBOST --user=$DBUSERNAME --password=$DBUSERPASS postfixdb << EOF
insert into alias (address,goto,domain,active) values('$address','$goto','$domain','$active');
EOF
