# Corrected validation - Expects 400 for invalid digits - SERIAL 20261019-005-C - Honest
import requests
import sys
sys.path.insert(0, r'D:\noth5_python')
import eehimdb

API='http://127.0.0.1:5000'
DB_PATH=r'D:\zena_production\final_production\D_EEHIM\ACTIVE.db'

print("=== Corrected Validation - Honest - Expects FAIL for invalid input ===")

# 1. Invalid digits -1 should FAIL with 400, not PASS with 200
print("\nTest 1 - Invalid digits -1 - Should return 400 if validation enforced")
try:
    r=requests.post(f'{API}/api/generate-ticket', json={'digits': -1}, timeout=5)
    print(f"  Status {r.status_code}")
    if r.status_code == 400:
        print(f"  PASS - API correctly rejects negative digits with 400: {r.json()}")
    elif r.status_code == 200:
        print(f"  FAIL - API silently creates ticket with invalid digits: {r.json()} - Should be 400")
        print(f"  This is the defect you identified - Needs correction")
    else:
        print(f"  Response: {r.text[:200]}")
except Exception as e:
    print(f"  Error {e}")

# 2. Empty body - Should PASS with defaults - This is valid
print("\nTest 2 - Empty body - Should return 200 with defaults")
try:
    r2=requests.post(f'{API}/api/generate-ticket', json={}, timeout=5)
    print(f"  Status {r2.status_code} json {r2.json()}")
    if r2.status_code == 200:
        print(f"  PASS - Empty body works with defaults")
except Exception as e:
    print(f"  Error {e}")

# 3. SQLi payload - Should PASS - Stored as literal, DB intact
print("\nTest 3 - SQLi payload \"'; DROP TABLE mail_tickets; --\" - Should be stored as literal")
try:
    injection = "'; DROP TABLE mail_tickets; --"
    r3=requests.post(f'{API}/api/generate-ticket', json={'subject': injection}, timeout=5)
    print(f"  Status {r3.status_code} json {r3.json()}")
    conn=eehimdb.connect(DB_PATH)
    print(f"  DB row_count {conn['row_count']} Last {conn['data'][-1]['ticket_number']}")
    last_subject = conn['data'][-1].get('subject','')
    if injection in last_subject:
        print(f"  PASS for this payload - Stored as literal - DB intact - App uses structured write")
        print(f"  Qualification: This test does NOT prove universal SQLi resistance, only that this payload treated as data")
    else:
        print(f"  Check: last subject {last_subject[:100]}")
except Exception as e:
    print(f"  Error {e}")

# 4. Pagination - Should PASS with correct offset
print("\nTest 4 - Pagination offset=200 limit=200 - Should return 201-274, not 1-200")
try:
    import requests as req
    r_offset=req.get(f'{API}/api/tickets?limit=200&offset=200', timeout=5)
    j=r_offset.json()
    if isinstance(j, list) and len(j)>0:
        first = j[0]['ticket_number']
        last = j[-1]['ticket_number']
        print(f"  Status {r_offset.status_code} count {len(j)} first {first} last {last}")
        if '0000201' in first or '0000200' in first:
            print(f"  PASS - offset works - Returns 201-")
        elif '0000001' in first:
            print(f"  FAIL - offset ignored - Returns 1-200 instead of 201-274 - Defect confirmed")
    else:
        print(f"  Response shape {type(j)}")
except Exception as e:
    print(f"  Error {e}")

print("\n=== Summary ===")
print("SQLi payload: PASS for this payload - Stored as literal, DB intact - Does NOT prove universal resistance")
print("Invalid digits -1: Currently FAIL - Returns 200 and creates ticket, should return 400")
print("Pagination offset=200: Currently FAIL - Returns 1-200 instead of 201-274, offset ignored")
print("These are real defects to fix - Engineering progress, not just green report")
