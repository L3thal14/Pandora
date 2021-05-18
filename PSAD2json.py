import requests
import os
from dotenv import load_dotenv
load_dotenv()
attackerLog = []
portLog = []
line_number = 0
attacker_line = 0
scanned_ports = 0
iptables = 0
with open('/var/log/psad/status.out', 'rt') as f:
    data = f.readlines()
for line in data:
    line_number += 1
    if line.__contains__('Top 25 attackers'):
        attacker_line = line_number
    if line.__contains__('Top 20 scanned ports'):
        scanned_ports = line_number
        print(data[scanned_ports])
    if line.__contains__('iptables log prefix counters'):
        iptables = line_number
i = attacker_line
while (i <= scanned_ports-3):
    attackerLog.append(data[i].replace("\n", "").strip())
    i += 1
j = scanned_ports
while(j < iptables-2):
    portLog.append(data[j].replace("\n", "").strip())
    j += 1
while("" in portLog):
    portLog.remove("")
VAR = os.getenv('DEPLOY_URL')
url = '{}portscanlogs'.format(VAR)
myobj = [{"attacker": attackerLog, "ports": portLog}]
requests.post(url, json=myobj)
