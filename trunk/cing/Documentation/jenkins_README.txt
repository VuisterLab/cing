https://wiki.jenkins-ci.org/display/JENKINS/Running+Jenkins+behind+Apache

org.jenkins-ci.plist.plist

# Use the .plist from $CINGROOT/scripts/cing for starting/stopping.
sudo launchctl load /Library/LaunchAgents/org.jenkins-ci.plist


# Or directly:
java -jar /Applications/Jenkins/jenkins.war --argumentsRealm.passwd.jurgenfd=XXXX --argumentsRealm.roles.jurgenfd=admin --httpPort=8081 --httpListenAddress=127.0.0.1 --ajp13Port=8010 --prefix=/jenkins



sloccount:
    port install sloccount
    
pylint:
    easy_install pylint  should give version 0.23.0 but fails to install for right python. TODO:
    mac ports gives 
    
nosetest:
    mac ports gives   py26-nose 1.0.0_0
    
# For selecting python 26 in mac ports.    
sudo port select --set python python26    
    