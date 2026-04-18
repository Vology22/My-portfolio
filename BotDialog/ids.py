import os
SESSIONS_DIR = "sessions"
fuck = ""
for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".session"):
            session_file = os.path.join(SESSIONS_DIR, filename)
            json_file = filename.replace(".session", "")
            fuck += json_file + "\n"

with open("sessions.txt", "w+") as f:
      f.write(fuck)