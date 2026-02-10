from algosdk.v2client import algod
import config
import base64

def get_algod_client():
    return algod.AlgodClient(config.ALGOD_TOKEN, config.ALGOD_ADDRESS)

def fetch_attendance_data(client, app_id, class_id):
    """
    Fetches attendance data for a specific class from the smart contract using Box Storage.
    Schema Assumption: 
    - Box Name: class_id (encoded as bytes)
    - Box Value: [Total Students (Uint64)][Present Students (Uint64)]
    """
    try:
        box_name = class_id.encode('utf-8')
        
        # specific call to fetch box content
        box_response = client.application_box_by_name(app_id, box_name)
        box_value = base64.b64decode(box_response['value'])
        
        # Parse 2 Uint64 integers (8 bytes each)
        if len(box_value) >= 16:
            total_students = int.from_bytes(box_value[:8], 'big')
            present_students = int.from_bytes(box_value[8:16], 'big')
            
            print(f"Fetched Box '{class_id}': Total={total_students}, Present={present_students}")
            
            return {
                "class_id": class_id,
                "total": total_students,
                "present": present_students
            }
        else:
            print(f"Error: Box '{class_id}' data length mismatch.")
            return None

    except Exception as e:
        # If box not found or other error
        print(f"Could not fetch attendance for {class_id}: {e}")
        return None
