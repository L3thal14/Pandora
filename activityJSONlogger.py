import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()
with open('/var/log/psad/honeypotslogger', 'rt') as f:
    data = f.readlines()
abcd = ""
for line in data:
    abcd += line + ","
jsonf = abcd.replace("""b'test'""", """'test'""")
finaljson = '[{"honeypots":[' + jsonf[:-1].replace("'", '"') + ']}]'
postjson = json.loads(finaljson)
VAR = os.getenv('DEPLOY_URL')
url = '{}honeypotlogs'.format(VAR)
requests.post(url, json=postjson)
print(url)
