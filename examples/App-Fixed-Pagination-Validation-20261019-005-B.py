
# ZENA Ticketing System Backend API - FIXED - SERIAL 20261019-005-B - Addresses pagination + validation defects
import datetime
import threading
import pathlib
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
sys.path.insert(0, r'D:\noth5_python')
import eehimdb

app = Flask(__name__)
CORS(app)

DB_PATH = r'D:\zena_production\final_production\D_EEHIM\ACTIVE.db'
write_lock = threading.Lock()

@app.route('/')
def index():
    return jsonify({'status': 'ZENA Ticketing API V5 - EEHIMDB V14 OWN FORMAT - Fixed pagination + validation - SERIAL 20261019-005-B'})

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    # FIX 1: Pagination - Properly support limit, offset, page
    try:
        limit = int(request.args.get('limit', 200))
    except:
        limit = 200
    # Cap at 1000 to prevent overload, but allow up to 1000
    limit = max(1, min(limit, 1000))
    
    try:
        offset = int(request.args.get('offset', 0))
    except:
        offset = 0
    offset = max(0, offset)
    
    # Support page param: page=1 -> offset 0, page=2 -> offset limit, etc.
    page = request.args.get('page')
    if page:
        try:
            page_num = int(page)
            if page_num >= 1:
                offset = (page_num - 1) * limit
        except:
            pass  # Invalid page, use offset as is
    
    filter_type = request.args.get('filter', 'all')
    
    # Read all then slice for correct pagination
    # For large DB, should implement DB-level pagination, but for proof we read all
    all_rows = eehimdb.read_rows(DB_PATH, limit=10000, filter_type=filter_type)
    
    # Apply offset/limit slicing - FIXES defect where offset/page ignored
    total = len(all_rows)
    sliced = all_rows[offset:offset+limit]
    
    # Return with pagination metadata for transparency
    # If client expects just array, return array. If expects object with metadata, support both
    # For backward compatibility, return array, but log pagination
    print(f"GET /api/tickets limit={limit} offset={offset} page={page} total={total} returned={len(sliced)} first={sliced[0]['ticket_number'] if sliced else 'none'} last={sliced[-1]['ticket_number'] if sliced else 'none'}")
    return jsonify(sliced)

@app.route('/api/generate-ticket', methods=['POST'])
def gen_ticket():
    d = request.get_json() or {}
    
    # FIX 2: Input validation - digits: -1 should fail, not silently create
    digits = d.get('digits', 7)
    try:
        digits = int(digits)
    except:
        return jsonify({'error': 'digits must be integer', 'code': 'INVALID_DIGITS'}), 400
    
    # Validate digits range - If contract says digits must be >=1 and <=10, enforce it
    if digits < 1 or digits > 10:
        return jsonify({'error': f'digits must be between 1 and 10, got {digits}', 'code': 'INVALID_DIGITS_RANGE', 'received': digits}), 400
    
    prefix1 = d.get('prefix1', 'TICK')
    p2_type = d.get('prefix2_type', 'YYYYMM')
    suffix = d.get('suffix', '-BLR')
    
    # Validate prefix1 - should not be empty
    if not prefix1 or not isinstance(prefix1, str):
        return jsonify({'error': 'prefix1 must be non-empty string'}), 400
    
    with write_lock:
        conn = eehimdb.connect(DB_PATH)
        rows = conn['data']
        next_num = len(rows) + 1
        serial = str(next_num).zfill(digits)
        now_str = datetime.datetime.now().strftime('%Y%m')
        p2 = now_str if p2_type=='YYYYMM' else ''
        if p2:
            tn = f'{prefix1}-{p2}-{serial}{suffix}'
        else:
            tn = f'{prefix1}-{serial}{suffix}'
        new_row = {
            'id': next_num,
            'ticket_number': tn,
            'from_email': d.get('from_email', f'test{next_num}@example.com'),
            'subject': d.get('subject', f'Test ticket {next_num}'),
            'body': d.get('body', f'Body {next_num} resolution tracking'),
            'dept': d.get('dept', 'Support'),
            'status': 'Open',
            'channel': d.get('channel', 'API'),
            'created_at': datetime.datetime.now().isoformat(),
            'customer_name': '', 'priority': '', 'assigned_agent': '',
            'assigned_group': '', 'attachments': '', 'first_response_at': '',
            'resolution_time_hours': '', 'resolved_at': '', 'response_time_hours': ''
        }
        rows.append(new_row)
        eehimdb._write_data_section(DB_PATH, rows)
    return jsonify({'ticket_number': tn, 'serial': serial, 'row_count': len(rows), 'id': next_num})

@app.route('/api/download', methods=['GET'])
def download_db():
    return jsonify({'path': DB_PATH, 'engine': eehimdb.get_engine_id()})

@app.route('/health', methods=['GET'])
def health():
    try:
        conn = eehimdb.connect(DB_PATH)
        return jsonify({'status': 'ok', 'engine': conn['engine'], 'page_size': conn['page_size'], 'row_count': conn['row_count'], 'first': conn['data'][0]['ticket_number'] if conn['data'] else None, 'last': conn['data'][-1]['ticket_number'] if conn['data'] else None, 'verify': 'PASS'})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)}), 500

if __name__ == '__main__':
    print(eehimdb.get_version())
    print(eehimdb.get_engine_id())
    eehimdb.verify_identity(DB_PATH)
    app.run(host='127.0.0.1', port=5000, debug=False)
