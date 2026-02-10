import time
import watcher
import analyzer
import responder
import config

def main():
    print("Starting VerifyU AI Engine...")
    
    # Initialize Algorand Client
    client = watcher.get_algod_client()
    print(f"Connected to node at {config.ALGOD_ADDRESS}")

    while True:
        print("\n--- Checking Attendance ---")
        try:
            # 1. Fetch Data
            # For now, we mock the class_id. In production, we'd loop through all classes.
            class_id = "class_101" 
            attendance_data = watcher.fetch_attendance_data(client, config.APP_ID, class_id)
            
            if attendance_data:
                print(f"Class {class_id}: {attendance_data['present']}/{attendance_data['total']} present.")

                # 2. Analyze
                is_critical = analyzer.analyze_attendance(
                    attendance_data['total'], 
                    attendance_data['present']
                )

                if is_critical:
                    print(f"ALERT: High absence detected for {class_id}!")
                    
                    # 3. Trigger Action
                    tx_id = responder.trigger_emergency_poll(config.APP_ID, class_id)
                    if tx_id:
                        print(f"Emergency Poll Triggered! TXID: {tx_id}")
                    else:
                        print("Failed to trigger poll.")
                else:
                    print("Attendance is within normal limits.")
            else:
                print("No data found or error fetching data.")

        except Exception as e:
            print(f"Error in main loop: {e}")

        # Sleep for 10 minutes (or 60s for demo)
        print("Sleeping...")
        time.sleep(60)

if __name__ == "__main__":
    main()
