# Apache NiFi custom action script for Azure HDInsight

This script deploys [Apache NiFi](http://nifi.apache.org) service on top of Azure HDInsight cluster.

* Nifi is deployed in clustered mode
* NiFi web interface is exposed on port 9099 (on every node it runs)
* Script allows deployment on either head or worker nodes
* Tested with NiFi v.1.3.0

## Installation 
Follow the the instructions in [Customize clusters using Script Action](https://docs.microsoft.com/en-us/azure/hdinsight/hdinsight-hadoop-customize-cluster-linux) article and use following Bash script URI:
```
https://raw.githubusercontent.com/MichalZylinski/HDIscripts/master/NiFi/nifi-deploy.sh
```