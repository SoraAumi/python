import requests

import json

response = requests.get("http://localhost:8080/modules/app/project/bp_user_bind.lsc?app_user_id=1833")

res = json.loads(response.text)

print(res)
