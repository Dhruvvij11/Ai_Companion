from datetime import datetime

def handle_time():
    print("Time tool called")
    now = datetime.now()
    return f"It’s {now.strftime('%I:%M %p').lstrip('0')}."
