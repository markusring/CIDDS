COLLECTOR_IP=YOUR_IP_ADDRESS
COLLECTOR_PORT=12345
TIMEOUT=45
sudo ovs-vsctl -- set Bridge br-int netflow=@nf --  --id=@nf  \
create  NetFlow  targets=\"${COLLECTOR_IP}:${COLLECTOR_PORT}\"  active-timeout=${TIMEOUT} 

sudo ovs-vsctl -- set Bridge br-tun netflow=@nf --  --id=@nf  \
create  NetFlow  targets=\"${COLLECTOR_IP}:${COLLECTOR_PORT}\"  active-timeout=${TIMEOUT} 

sudo ovs-vsctl -- set Bridge br-ex netflow=@nf --  --id=@nf  \
create  NetFlow  targets=\"${COLLECTOR_IP}:${COLLECTOR_PORT}\"  active-timeout=${TIMEOUT} 
