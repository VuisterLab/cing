org.jenkins-ci.plist.plist

# Use the .plist from scripts/cing
sudo launchctl unload /Library/LaunchAgents/org.jenkins-ci.plist
# or directly:
java -jar /Applications/Jenkins/jenkins.war --httpListenAddress=localhost --httpPort=8081 \
    --argumentsRealm.passwd.jurgenfd=xx --argumentsRealm.roles.jurgenfd=admin

Installation thru Tomcat:

https://wiki.jenkins-ci.org/display/JENKINS/Tomcat