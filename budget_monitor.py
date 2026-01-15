import os
import json
from datetime import datetime, timedelta
import safe_zone

def load_history():
    if os.path.exists(safe_zone.USAGE_LOG_FILE):
        try:
            with open(safe_zone.USAGE_LOG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_run(start_time, end_time):
    history = load_history()
    
    # Calculate duration in seconds
    duration = (end_time - start_time).total_seconds()
    
    # NEON BILLING FORMULA:
    # Actual Run Time + 5 Minute "Cool Down"
    # Note: Even if we open/close connection quickly, the endpoint stays active for 5 mins.
    # We should track "Endpoint Active Window", but assuming 1 run = 1 activation is safe for this ETL.
    billable_seconds = duration + (safe_zone.AUTOSUSPEND_MINUTES * 60)
    
    entry = {
        "timestamp": start_time.isoformat(),
        "duration_sec": round(duration, 2),
        "billable_sec": round(billable_seconds, 2)
    }
    
    history.append(entry)
    
    # Keep file size small (last 1000 runs only)
    if len(history) > 1000:
        history = history[-1000:]
        
    with open(safe_zone.USAGE_LOG_FILE, 'w') as f:
        json.dump(history, f, indent=2)
        
    return entry

def check_budget_status():
    history = load_history()
    if not history:
        return
        
    # Filter for CURRENT MONTH only
    now = datetime.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    total_billable_seconds = 0
    for run in history:
        try:
            run_date = datetime.fromisoformat(run['timestamp'])
            if run_date >= current_month_start:
                total_billable_seconds += run['billable_sec']
        except (ValueError, KeyError):
            continue
            
    # Convert to CU-Hours
    # (Seconds / 3600) * 0.25 CU
    hours_active = total_billable_seconds / 3600
    cu_used = hours_active * safe_zone.MIN_COMPUTE_CU
    
    percent_used = (cu_used / safe_zone.MONTHLY_QUOTA_CU_HOURS) * 100
    
    print(f"\n💰 BUDGET ESTIMATE (Month-to-Date):")
    print(f"   - Active Hours: {round(hours_active, 2)} hrs")
    print(f"   - CU Usage:     {round(cu_used, 2)} / {safe_zone.MONTHLY_QUOTA_CU_HOURS} CU-Hrs")
    print(f"   - Status:       {round(percent_used, 1)}% Used")
    
    if percent_used > 80:
        print("   ⚠️ WARNING: You are approaching your monthly limit!")

if __name__ == "__main__":
    check_budget_status()
