#!/bin/bash -v

#
# Sets up an SSH tunnel through a gateway server
# then starts a Hudson slave on the target host
#
# Written by: mattkreadytalk@java.net ?
# Original name: ssh-gateway-slave
# Rewritten by: JFD.
# Add to the node configuration where it reads:
#       Launch method: "Launch slave via execution of command on the Master"
#           Launch command:
# for NMRpro:
#       /home/i/workspace/cingStable/scripts/jenkins/ssh-gateway-slave-jenkins.sh www.cmbi.ru.nl jurgend nmrpro.cmbi.umcn.nl jd /Users/jd/workspace/jenkins/slave.jar
# or for NMRproVC
#       /home/i/workspace/cingStable/scripts/jenkins/ssh-gateway-slave-jenkins.sh www.cmbi.ru.nl jurgend  vcnmr.cmbi.umcn.nl  i   /home/i/workspace/jenkins/slave.jar
# or for LVCa
#       /home/i/workspace/cingStable/scripts/jenkins/ssh-gateway-slave-jenkins.sh 143.210.182.231     jurgen 10.1.182.220         i   /home/i/workspace/jenkins/slave.jar
#       /home/i/workspace/cingStable/scripts/jenkins/ssh-gateway-slave-jenkins.sh gate1.nmrc.le.ac.uk jurgen lvca                 i   /home/i/workspace/jenkins/slave.jar
#

if [ $# -ne 5 ]
then
  echo "Usage: $0  <ssh-gateway-user> <ssh-gateway-host>       <ssh-target-user> <ssh-target-host>       <jarFile>"
  exit 1
fi

gateway=$1
gatewayUser=$2
target=$3
targetUser=$4
# Change this location you may. 
#targetJarFile=/home/i/workspace/jenkins/slave.jar
targetJarFile=$5
jarFile="/home/i/workspace/jenkins/slave.jar"

echo "Setup ssh keys you did?"
echo "DEBUG: gateway        $gateway" 
echo "DEBUG: gatewayUser    $gatewayUser" 
echo "DEBUG: target         $target"
echo "DEBUG: targetUser     $targetUser"
echo "DEBUG: jarFile        $jarFile"
echo "DEBUG: targetJarFile  $targetJarFile"
 
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
ssh -N -L localhost:${port}:${target}:22 ${gatewayUser}@${gateway} &
tunnelpid=$!

# Give the tunnel some time
sleep 2

# Copy and start the slave jar
scp -P ${port} -o StrictHostKeyChecking=no -o HostKeyAlias=${target} ${jarFile} $targetUser@localhost:${targetJarFile}
ssh -p ${port} -o StrictHostKeyChecking=no -o HostKeyAlias=${target}            $targetUser@localhost "hostname; java -jar $targetJarFile"
