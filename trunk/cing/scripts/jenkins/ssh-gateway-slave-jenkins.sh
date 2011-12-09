#!/bin/bash -v

#
# Sets up an SSH tunnel through a gateway server
# then starts a Hudson slave on the target host
#
# Written by: mattkreadytalk@java.net ?
# Original name: ssh-gateway-slave
# Rewritten by: JFD.

if [ $# -ne 2 ]
then
  echo "Usage: $0 <ssh-gateway> <ssh-target>"
  exit 1
fi

gateway=$1
target=$2
jarFile="/home/i/workspace/jenkins/slave.jar"
targetJarFile="/Users/jd/workspace35/jenkins/slave.jar"
targetUser="jd"

echo "DEBUG: gateway $gateway" 
echo "DEBUG: target  $target"
echo "DEBUG: jarFile $jarFile"
 
tunnelpid=0

minport=42000
maxport=45000

# Provide for tunnel cleanup
function cleanup {
  [ ${tunnelpid} -ne 0 ] && kill ${tunnelpid} > /dev/null 2>&1
}
trap "cleanup" SIGINT SIGTERM EXIT

# Find an open port
port=0
openports=$(netstat -lnt 2>&1 | grep tcp | grep -v tcp6 | awk '{print $4}' | awk -F: '{print $2}' | xargs echo -n)
for port in $(seq ${minport} ${maxport})
do
  if ! [[ "${openports}" =~ "${port}" ]]
  then
    break
  fi
done

echo "DEBUG: opening port $port"

# Create a tunnel
ssh -N -L localhost:${port}:${target}:22 ${gateway} &
tunnelpid=$!

# Give the tunnel some time
sleep 2

# Copy and start the slave jar
scp -P ${port} -o StrictHostKeyChecking=no -o HostKeyAlias=${target} ${jarFile} $targetUser@localhost:${targetJarFile}
ssh -p ${port} -o StrictHostKeyChecking=no -o HostKeyAlias=${target}            $targetUser@localhost "hostname; java -jar $targetJarFile"
