import time

IDLE_THRESHOLD = 15 * 60
IDLE_COOLDOWN = 20 * 60

def should_trigger_idle(state):
    now = time.time()

    if now - state.last_user_time > IDLE_THRESHOLD:
        if now - state.last_idle_prompt > IDLE_COOLDOWN:
            state.last_idle_prompt = now
            return True

    return False
