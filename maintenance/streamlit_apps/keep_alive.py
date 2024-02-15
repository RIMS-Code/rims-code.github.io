# Query all `app.json` apps with requests and print the status code of the response

import json
import sys

import requests

apps = json.loads(open("apps.json", "r").read())

any_down = False

for key in apps:
    res = requests.get(apps[key])
    print(f"{key}: {'OK' if res.ok else 'DOWN'}")
    if not res.ok:
        any_down = True

# Exit with 1 if any app is down, this will fail the GitHub action
if any_down:
    sys.exit(1)
