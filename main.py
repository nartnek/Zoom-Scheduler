import os, sys, time, datetime, subprocess, json, logging
import pyautogui
import schedule

# Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

CONFIG_DIR = "./config"
MEETINGS_FILE = os.path.join(CONFIG_DIR, "meetings.json")

# Load UI elements and paths
try:
    UI = {k: os.path.join('assets', v) for k, v in json.load(open(os.path.join(CONFIG_DIR, 'ui_elements.json'), 'r', encoding='utf-8')).items()}
    paths = json.load(open(os.path.join(CONFIG_DIR, 'paths.json'), 'r', encoding='utf-8'))
except (FileNotFoundError, json.JSONDecodeError) as e:
    logging.error("Config load failed: %s", e)
    sys.exit(1)

pyautogui.PAUSE = 0.15
pyautogui.FAILSAFE = True

CONFIDENCE = 0.87

# meeting persistence
def load_meetings():
    """Load meetings from JSON if available, else None."""
    if os.path.exists(MEETINGS_FILE):
        try:
            with open(MEETINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning("Could not read %s: %s", MEETINGS_FILE, e)
    return None

def save_meetings(meetings):
    """Save meetings to JSON."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(MEETINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(meetings, f, indent=2)
    logging.info("Saved %d meetings to %s", len(meetings), MEETINGS_FILE)

# interactive prompt
def get_user_meetings():
    """Interactively collect meeting info from the user."""
    meetings = []
    try:
        n = int(input("How many meetings would you like to schedule? "))
    except ValueError:
        print("That's not a number. Exiting.")
        sys.exit(1)

    valid_days = ('mon','tue','wed','thu','fri','sat','sun')
    for i in range(1, n+1):
        print(f"\n--- Meeting #{i} ---")
        name     = input("  Name (for your reference): ").strip()
        m_id     = input("  Zoom Meeting ID: ").strip()
        passwd   = input("  Passcode (leave blank if none): ").strip()
        days_in  = input("  Days (e.g. mon,wed,fri): ").lower().replace(' ', '')
        days_raw = [d for d in days_in.split(',') if d]
        start    = input("  Start time (HH:MM, 24h): ").strip()
        try:
            dur = int(input("  Duration (minutes): ").strip())
        except ValueError:
            print("  Invalid duration; defaulting to 60 min.")
            dur = 60

        days = [d for d in days_raw if d in valid_days]
        if not days:
            print("  No valid days given; defaulting to 'mon'.")
            days = ['mon']

        meetings.append({
            'name':     name or f"Meeting #{i}",
            'id':       m_id,
            'passwd':   passwd,
            'days':     days,
            'start':    start,
            'duration': dur
        })
    return meetings

# scheduling
def schedule_meetings(meetings):
    day_map = {
        'mon': schedule.every().monday,
        'tue': schedule.every().tuesday,
        'wed': schedule.every().wednesday,
        'thu': schedule.every().thursday,
        'fri': schedule.every().friday,
        'sat': schedule.every().saturday,
        'sun': schedule.every().sunday,
    }
    for m in meetings:
        for d in m['days']:
            day_map[d].at(m['start']).do(lambda m=m: run_meeting(m))
            logging.info("Scheduled '%s' on %s at %s for %s min",
                         m['name'], d.title(), m['start'], m['duration'])

# (keep your join/leave/run_meeting logic here unchanged)

if __name__ == "__main__":
    print("\nWelcome to Zoom Scheduler")

    meetings = load_meetings()
    if meetings:
        print(f"Loaded {len(meetings)} meetings from {MEETINGS_FILE}")
    else:
        meetings = get_user_meetings()
        save_meetings(meetings)

    schedule_meetings(meetings)
    print("\nScheduler running. Press Ctrl+C to stop.\n")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down. Bye!")
