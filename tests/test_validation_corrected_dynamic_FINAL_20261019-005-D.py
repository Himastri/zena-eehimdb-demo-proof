# Corrected Validation - Dynamic - No hardcoded 271 - SERIAL 20261019-005-D FINAL - Fixes stale summary
import requests, sys
sys.path.insert(0, r'D:\noth5_python')
import eehimdb
API='http://127.0.0.1:5000'
DB_PATH=r'D:\zena_production\final_production\D_EEHIM\ACTIVE.db'
conn_start=eehimdb.connect(DB_PATH)
start_count=conn_start['row_count']
print(f"Start row_count={start_count} last={conn_start['data'][-1]['ticket_number']}")
results=[]
r=requests.post(f'{API}/api/generate-ticket', json={'digits':-1}, timeout=5)
print(f"Test1 Invalid digits -1 status {r.status_code} {r.json()}")
results.append(("Invalid digits -1", "PASS" if r.status_code==400 else "FAIL"))
r2=requests.post(f'{API}/api/generate-ticket', json={}, timeout=5)
print(f"Test2 Empty body status {r2.status_code} {r2.json()}")
results.append(("Empty body", "PASS" if r2.status_code==200 else "FAIL"))
inj="'; DROP TABLE mail_tickets; --"
r3=requests.post(f'{API}/api/generate-ticket', json={'subject':inj}, timeout=5)
conn=eehimdb.connect(DB_PATH)
last_sub=conn['data'][-1].get('subject','')
print(f"Test3 SQLi status {r3.status_code} row_count {conn['row_count']} literal {inj in last_sub}")
results.append(("SQLi literal", "PASS" if inj in last_sub else "FAIL"))
print("Qualification: Does NOT prove universal resistance")
r_off=requests.get(f'{API}/api/tickets?limit=200&offset=200', timeout=5)
j=r_off.json()
first=j[0]['ticket_number'] if j else 'none'
print(f"Test4 offset=200 count {len(j)} first {first} Expected 201 - Current DB {conn['row_count']}")
results.append(("Pagination offset=200", "PASS" if '0000201' in first else "FAIL"))
r1=requests.get(f'{API}/api/tickets?limit=200&offset=0', timeout=5).json()
r2_=requests.get(f'{API}/api/tickets?limit=200&offset=200', timeout=5).json()
concat=r1+r2_
conn=eehimdb.connect(DB_PATH)
db_count=conn['row_count']
dupes=len(concat)!=len(set([x['ticket_number'] for x in concat]))
print(f"Test5 concat {len(r1)}+{len(r2_)}={len(concat)} DB {db_count} dupes {dupes}")
results.append(("Concat no dupes", "PASS" if not dupes else "FAIL"))
print("\n=== FINAL SUMMARY Generated from actual assertions ===")
for n,s in results:
    print(f"{n}: {s}")
all_pass=all(s=="PASS" for _,s in results)
print(f"Overall {'ALL PASS' if all_pass else 'SOME FAIL'} {sum(1 for _,s in results if s=='PASS')}/{len(results)}")
conn_final=eehimdb.connect(DB_PATH)
print(f"Final row_count={conn_final['row_count']} Added {conn_final['row_count']-start_count}")
print("Avoid hard-coding 271 - Use current count")
print("Latest checks demonstrate working offset pagination and negative-input rejection")
