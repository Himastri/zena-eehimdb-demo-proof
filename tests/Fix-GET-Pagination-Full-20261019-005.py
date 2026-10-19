
# Fix GET pagination - Support limit up to 1000 + offset + page - SERIAL 20261019-005
import pathlib
path = pathlib.Path(r'D:\zena_production\zena_ticketing_system\backend\api\app.py')
text = path.read_text(encoding='utf-8', errors='ignore')

# Find get_tickets function and replace
import re

# Replace the get_tickets function entirely with version supporting limit, offset, page
old_pattern = r"@app\.route\('/api/tickets'.*?def get_tickets\(\):.*?return jsonify\(.*?\)"

# Simpler: find def get_tickets and replace until next def or route
lines = text.splitlines()
new_lines = []
in_get = False
skip = False
fixed = False

for i, line in enumerate(lines):
    if "@app.route('/api/tickets'" in line or '@app.route("/api/tickets"' in line:
        in_get = True
        # Write new fixed version
        if not fixed:
            new_lines.append("@app.route('/api/tickets', methods=['GET'])")
            new_lines.append("def get_tickets():")
            new_lines.append("    limit = int(request.args.get('limit', 200))")
            new_lines.append("    # Cap at 1000 to prevent overload, but allow up to 1000 for full retrieval")
            new_lines.append("    limit = min(limit, 1000)")
            new_lines.append("    offset = int(request.args.get('offset', 0))")
            new_lines.append("    page = request.args.get('page')")
            new_lines.append("    if page:")
            new_lines.append("        try:")
            new_lines.append("            page_num = int(page)")
            new_lines.append("            offset = (page_num - 1) * limit")
            new_lines.append("        except:")
            new_lines.append("            pass")
            new_lines.append("    filter_type = request.args.get('filter', 'all')")
            new_lines.append("    all_rows = eehimdb.read_rows(DB_PATH, limit=10000, filter_type=filter_type)  # Read all then slice")
            new_lines.append("    # Apply offset/limit slicing for pagination")
            new_lines.append("    sliced = all_rows[offset:offset+limit]")
            new_lines.append("    return jsonify(sliced)")
            new_lines.append("")
            fixed = True
            skip = True
        continue
    if in_get and skip:
        # Skip old function body until return jsonify
        if "return jsonify" in line and "sliced" not in line and "all_rows" not in line:
            # This is end of old function, stop skipping
            in_get = False
            skip = False
            continue
        if line.strip().startswith("@app.route") or (line.strip().startswith("def ") and "get_tickets" not in line):
            # Next route/def, stop skipping and add this line
            in_get = False
            skip = False
            new_lines.append(line)
            continue
        # Otherwise skip
        continue
    new_lines.append(line)

if fixed:
    path.write_text("\n".join(new_lines), encoding='utf-8')
    print("Fixed GET /api/tickets to support limit up to 1000 + offset + page")
    # Verify
    text2 = path.read_text()
    for l in text2.splitlines():
        if "def get_tickets" in l or "limit = int(request.args.get" in l or "offset" in l.lower() and "def " not in l:
            print(l)
else:
    print("Failed to fix - pattern not found")
    for l in lines:
        if "/api/tickets" in l:
            print(l)
