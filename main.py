import time
import datetime
import subprocess
import pyautogui
import schedule
import json

# Load UI‐element image names and Zoom path
UI = {
    k: './assets/' + v
    for k, v in json.load(open('./config/ui_elements.json')).items()
}
paths = json.load(open('./config/paths.json'))

def wait_for(elem, timeout=30):
    """Wait up to `timeout` seconds for the UI element image to appear."""
    end = time.time() + timeout
    while time.time() < end:
        loc = pyautogui.locateOnScreen(UI[elem])
        if loc:
            return loc
        time.sleep(0.2)
    raise RuntimeError(f"Element '{elem}' not found on screen")

def join(meeting):
    """Open Zoom and join the specified meeting."""
    subprocess.Popen(executable=paths['zoom'])
    btn = wait_for('join')
    pyautogui.click(pyautogui.center(btn))
    wait_for('join-box')
    pyautogui.typewrite(meeting['id'], interval=0.05)
    pyautogui.press('enter')
    wait_for('passcode')
    pyautogui.typewrite(meeting['passwd'], interval=0.05)
    pyautogui.press('enter')

def leave():
    """Leave the current Zoom meeting."""
    btn0 = wait_for('leave0')
    pyautogui.click(pyautogui.center(btn0))
    time.sleep(0.5)
    btn1 = wait_for('leave')
    pyautogui.click(pyautogui.center(btn1))

def run_meeting(meeting):
    t0 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{t0}] Joining '{meeting['name']}'")
    join(meeting)
    time.sleep(meeting['duration'] * 60)
    leave()
    t1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{t1}] Left '{meeting['name']}'")

def get_user_meetings():
    """Interactively collect meeting info from the user."""
    meetings = []
    try:
        n = int(input("How many meetings would you like to schedule? "))
    except ValueError:
        print("That's not a number. Exiting.")
        exit(1)

    for i in range(1, n+1):
        print(f"\n--- Meeting #{i} ---")
        name     = input("  Name (for your reference): ").strip()
        m_id     = input("  Zoom Meeting ID: ").strip()
        passwd   = input("  Passcode (leave blank if none): ").strip()
        days_raw = input("  Days (e.g. mon,wed,fri): ").lower().split(',')
        start    = input("  Start time (HH:MM, 24h): ").strip()
        try:
            dur = int(input("  Duration (minutes): ").strip())
        except ValueError:
            print("  Invalid duration; defaulting to 60 min.")
            dur = 60

        meetings.append({
            'name':     name,
            'id':       m_id,
            'passwd':   passwd,
            'days':     [d for d in days_raw if d in ('mon','tue','wed','thu','fri','sat','sun')],
            'start':    start,
            'duration': dur
        })
    return meetings

def schedule_meetings(meetings):
    """Register all meetings with the `schedule` library."""
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
            day_map[d].at(m['start']).do(run_meeting, m)
            print(f"Scheduled '{m['name']}' on {d.title()} at {m['start']} for {m['duration']} min")

if __name__ == "__main__":
    print("\nWelcome to Zoom Scheduler")
    meetings = get_user_meetings()
    schedule_meetings(meetings)
    print("\nScheduler running. Press Ctrl+C to stop.\n")
    while True:
        schedule.run_pending()
        time.sleep(30)