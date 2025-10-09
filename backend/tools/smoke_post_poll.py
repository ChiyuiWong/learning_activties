import requests
url='http://127.0.0.1:5000/api/learning/polls'
payload={"question":"Smoke test poll from script","options":["One","Two","Three"],"course_id":"COMP5241"}
try:
    r=requests.post(url,json=payload,timeout=5)
    print('status',r.status_code)
    try:
        print('json',r.json())
    except Exception as e:
        print('no json',r.text[:200])
except Exception as e:
    print('error',e)
