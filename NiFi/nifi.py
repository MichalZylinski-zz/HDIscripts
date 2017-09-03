#!/usr/bin/python

import xml.etree.ElementTree as ET
import subprocess, os, socket, string, random

#finding zookeeper names
def get_zookeeper_hostnames():
	tree = ET.parse("/etc/hadoop/conf/yarn-site.xml")
	root = tree.getroot()
	return [p.find('value').text for p in root.findall("property") if p.find('name').text == "hadoop.registry.zk.quorum"][0]

def get_random_key(size=32):
	chars = string.letters+string.digits
	return "".join(random.choice(chars) for i in xrange(size))


PACKAGE_NAME = "nifi-1.3.0-bin.tar.gz"
#PACKAGE_LOCATION = "https://michalz.blob.core.windows.net/hdiscripts/"
PACKAGE_LOCATION = "http://www-eu.apache.org/dist/nifi/1.3.0/"
ZOOKEEPER_HOSTNAMES = get_zookeeper_hostnames()
WEBSERVER_PORT = 9099
CLUSTER_PROTOCOL_PORT = 16666
SECRET_KEY = get_random_key()

print "Downloading package...", 
cmd = "wget %s%s -O /tmp/%s" % (PACKAGE_LOCATION, PACKAGE_NAME, PACKAGE_NAME)
print cmd
cmd = cmd.split(" ")
subprocess.call(cmd)
print "done."

os.chdir("/tmp")
print "Unpacking package...", 
cmd = "tar -xf " + PACKAGE_NAME
cmd = cmd.split(" ")
subprocess.call(cmd)
print "done."

print "Moving package...", 
cmd = "rm -rf /usr/nifi".split(" ")
subprocess.call(cmd)
cmd = "mkdir /usr/nifi"
cmd = cmd.split(" ")
subprocess.call(cmd)
cmd = "mv /tmp/nifi-1.3.0/* /usr/nifi"
subprocess.call(cmd, shell=True)
print "done."

os.remove("/tmp/"+PACKAGE_NAME)

print "Modifying NiFi configuration..."
#modifying nifi.properties
new_config = open("/usr/nifi/conf/nifi.properties.new", "w")
with open("/usr/nifi/conf/nifi.properties", "r") as f:	
	for line in f:
		if line.find("nifi.web.http.host") == 0:
			line = "nifi.web.http.host="+socket.gethostbyname(socket.gethostname())
		if line.find("nifi.web.http.port") == 0:
			line = "nifi.web.http.port=%s\n" % WEBSERVER_PORT
		if line.find("nifi.cluster.is.node") == 0:
			line = "nifi.cluster.is.node=true\n"
		if line.find("nifi.cluster.node.address") == 0:
			line = "nifi.cluster.node.address="+str(socket.getfqdn())+"\n"
		if line.find("nifi.cluster.node.protocol.port") == 0:
			line = "nifi.cluster.node.protocol.port="+str(CLUSTER_PROTOCOL_PORT)+"\n"
		if line.find("nifi.zookeeper.connect.string") == 0:
			line = "nifi.zookeeper.connect.string="+ZOOKEEPER_HOSTNAMES+"\n"
		if line.find("nifi.sensitive.props.key") == 0:
			line = "nifi.sensitive.props.key="+SECRET_KEY+"\n"
		new_config.write(line)

new_config.close()
os.rename("/usr/nifi/conf/nifi.properties.new", "/usr/nifi/conf/nifi.properties")

#modifying state-management.xml
sm_config = ET.parse("/usr/nifi/conf/state-management.xml")
root = sm_config.getroot()
connect_string = [p for p in root.find("cluster-provider").findall("property") if p.get('name')=="Connect String"][0]
connect_string.text = ZOOKEEPER_HOSTNAMES
sm_config.write("/usr/nifi/conf/state-management.xml")
print "done."
print "Starting Nifi server...",
cmd = "/usr/nifi/bin/nifi.sh start &"
cmd = cmd.split(" ")
subprocess.Popen(cmd)

