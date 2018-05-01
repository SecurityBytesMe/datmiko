# datmiko

Datmiko (DevOps Automation Tool Miko) leverages netmiko and multiprocessing to bring you parallelism to your network configurations.

### Download & Setup
* git clone https://github.com/ChristopherAnders/datmiko/blob/master/datmiko.py
* pip install -r requirements.txt 
* python datmiko.py -h 

## Examples
```
$ python datmiko.py -u admin -p PASS -d cisco_ios 
$ python datmiko.py -u admin -p PASS -s switch-1 switch-2 switch-3
$ python datmiko.py -u admin -p PASS -f switches.txt
```

## changing command(s) ran on switches
in `datmiko.py` find `commands` variable and change this to what you want
```
commands = ['ip domain-name example.com',
            'ip name-server IPADDRESS',
            'ip name-server IPADDRESS',
            'no ntp server IPADDRESS',
            'no ntp server IPADDRESS',
            'ntp server example-clock.com prefer',
            'ntp server example-ipv6clock.example.com',
            'write memory']
```
