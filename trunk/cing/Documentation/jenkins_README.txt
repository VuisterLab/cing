######################################################################################################################
# Installation under Ubuntu use:
######################################################################################################################
http://pkg.jenkins-ci.org/debian/
and then configuration details are at:
https://wiki.jenkins-ci.org/display/JENKINS/Installing+Jenkins+on+Ubuntu
# Make sure not to install virtual hosts.
# Add proxies instead to:
sudo vi /etc/apache2/httpd.conf 
# configure to use port 8081 instead of the default 8080 which is already in use for tomcat.
# also add prefix and listen address.
vi /etc/default/jenkins
# Start
sudo /etc/init.d/jenkins restart
# Log
tail -f /var/log/jenkins/jenkins.log &
# Disable Jenkins
# Found on http://superuser.com/questions/266040/how-do-you-disable-an-upstart-service-in-ubuntu-10-10
chkconfig --list | grep -i jenk 
# Next command will generate lots of warnings to be ignored.
chkconfig -s jenkins off
chkconfig --list | grep -i jenk 

# Install deps such as:
sudo apt-get remove python-coverage python-nose
sudo easy_install nose

######################################################################################################################
# Installation on Mac:
######################################################################################################################

https://wiki.jenkins-ci.org/display/JENKINS/Running+Jenkins+behind+Apache

# Note that Jenkins on Java 1.5 was not functioning right. It had many console messages like:
NoClassDefFoundError: at hudson.model.Hudson.getComputer

org.jenkins-ci.plist.plist

# Use the .plist from $CINGROOT/scripts/cing for starting/stopping.
# Use the -w flag to override the disabled parameter in the plist.
# Normally jenkins on development is disabled.
sudo launchctl   load -w /Library/LaunchAgents/org.jenkins-ci.plist
sudo launchctl unload -w /Library/LaunchAgents/org.jenkins-ci.plist


# Or directly:
java -jar /Applications/Jenkins/jenkins.war --argumentsRealm.passwd.jurgenfd=XXXX --argumentsRealm.roles.jurgenfd=admin \
    --httpPort=8081 --httpListenAddress=127.0.0.1 --ajp13Port=8010 --prefix=/jenkins


# mac ports gives pylint-2.6 0.23.0 (only recently; this was 0.20 which was a real pain in the..)
# mac ports gives py26-nose  1.0.0_0

port install sloccount py26-lint py26-nose py26-coverage
    
# Rename to version aspecifics for easy of code maintenance.
    cd /opt/local/bin
    sudo ln -s coverage-2.6    coverage
    sudo ln -s nosetests-2.6   nosetests
    sudo ln -s pylint-2.6      pylint
