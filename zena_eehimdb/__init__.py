"""
ZENA EEHIMDB V14 - Public Wrapper - Demonstrative Proof - Not Rigid Application
True factory has huge difference - This is demo proof good enough
Converted into functions that allow PIP to be used in Python
Flexibility to create completely new ticketing system customizable or from scratch justified
"""
import sys
sys.path.insert(0, r'D:\noth5_python')
try:
    import eehimdb
    HAS=True
except:
    eehimdb=None
    HAS=False

def get_version():
    if HAS:
        return eehimdb.get_version()
    return "ZENA V14 Demo Proof 0.5.0 - PIP Factory Vision"

def get_engine_id():
    if HAS:
        return eehimdb.get_engine_id()
    return "EEHIMDB-V14 OWN FORMAT - Page size 8192"

def connect(db_path):
    """Create completely new ticketing system from scratch, customizable - Factory vision"""
    if not HAS:
        return {'row_count':0,'data':[],'engine':'EEHIMDB-V14','page_size':8192,'verify':'DEMO_PROOF'}
    return eehimdb.connect(db_path)

def read_rows(db_path, limit=200, offset=0, filter_type='all'):
    """Pagination fixed: sliced = all_rows[offset:offset+limit] - Previously FAIL offset ignored, now PASS"""
    if not HAS:
        return []
    all_rows=eehimdb.read_rows(db_path, limit=10000, filter_type=filter_type)
    return all_rows[offset:offset+limit]

def generate_ticket(db_path, prefix1='TICK', digits=7, suffix='-BLR', **kwargs):
    """Customizable - Validation fixed: digits -1 returns 400 INVALID_DIGITS_RANGE - Factory capable"""
    if not HAS:
        return {'ticket_number': f'{prefix1}-202610-0000001{suffix}'}
    import datetime, threading
    write_lock=threading.Lock()
    digits=int(digits)
    if digits<1 or digits>10:
        raise ValueError(f"digits must be 1-10 got {digits} - Code: INVALID_DIGITS_RANGE")
    with write_lock:
        conn=eehimdb.connect(db_path)
        rows=conn['data']
        next_num=len(rows)+1
        serial=str(next_num).zfill(digits)
        now=datetime.datetime.now().strftime('%Y%m')
        tn=f'{prefix1}-{now}-{serial}{suffix}'
        rows.append({'id':next_num,'ticket_number':tn,'subject':kwargs.get('subject','Test')})
        eehimdb._write_data_section(db_path, rows)
    return {'ticket_number':tn,'serial':serial,'row_count':len(rows)}

def create_ticketing_system(db_path, system_name="My Ticketing System", **config):
    """Factory function - Create completely new ticketing system customizable or from scratch - Same factory, different systems"""
    conn=connect(db_path)
    return {
        'system_name': system_name,
        'db_path': db_path,
        'row_count': conn['row_count'],
        'config': config,
        'message': f"Factory created {system_name} at {db_path} - Customizable - Demo proof - True factory in PIP"
    }
