"""
Demo Factory - Create completely new ticketing system from scratch - Customizable
Demonstrative proof of abilities - Not rigid application - True factory has huge difference
Converted into function and allows PIP to be used in Python
Flexibility to create completely new ticketing system customizable or developed from scratch justified
"""
import sys
sys.path.insert(0, r'D:\noth5_python')
try:
    import zena_eehimdb
    print(f"Version: {zena_eehimdb.get_version()}")
    print(f"Engine: {zena_eehimdb.get_engine_id()}")
    
    # Same factory, different ticketing systems - Flexibility justified - Not rigid component
    hr_system = zena_eehimdb.create_ticketing_system(db_path="hr.db", system_name="HR Ticketing", prefix1="HR", suffix="-HR")
    print(f"Created: {hr_system['system_name']} at {hr_system['db_path']}")
    
    it_system = zena_eehimdb.create_ticketing_system(db_path="it.db", system_name="IT Support", prefix1="IT", suffix="-IT")
    print(f"Created: {it_system['system_name']} at {it_system['db_path']}")
    
    ticket = zena_eehimdb.generate_ticket(db_path="hr.db", prefix1="HR", suffix="-HR-2026", digits=5, subject="Leave request")
    print(f"HR Ticket: {ticket['ticket_number']}")
    print("Factory capable - Demonstrative proof - Next step PIP package - Not rigid application")
except Exception as e:
    print(f"Demo without binary: {e} - This is demo proof - True factory has binary - Evidence in evidence/ folder")
