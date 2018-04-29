# datmiko

Datmiko (DevOps Automation Tool Miko) leverages netmiko and multiprocessing to bring you parallelism to your network configurations.

### Download & Setup
* git clone https://github.com/ChristopherAnders/datmiko/blob/master/datmiko.py
* pip install -r requirements.txt 
* python datmiko.py -h 

## Examples
$ python datmiko.py -u admin -p PASS -d cisco_ios 
$ python datmiko.py -u admin -p PASS -s switch-1 switch-2 switch-3
$ python datmiko.py -u admin -p PASS -f switches.txt
