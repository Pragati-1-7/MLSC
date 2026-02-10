import config

def analyze_attendance(total_students, present_students):
    """
    Returns True if absence rate > Threshold (e.g., 40%).
    """
    if total_students == 0:
        return False
        
    absence_rate = (total_students - present_students) / total_students
    
    print(f"Absence Rate: {absence_rate:.2%}")
    
    return absence_rate > config.ABSENCE_THRESHOLD
