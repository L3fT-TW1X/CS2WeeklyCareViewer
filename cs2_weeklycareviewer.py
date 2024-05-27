import requests
import json
import os
from datetime import datetime, timedelta
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox, Canvas
from PIL import Image, ImageTk


# Configuration
STEAM_API_KEY = 'PUT YOUR STEAM WEB API HERE'  # Replace with your Steam API key
ACCOUNT_FILE = 'cs2_accounts.json' # Path to local account data file
BACKGROUND_IMAGE_PATH = 'Fonts/background.png'  # Path to background image
ICON_PATH = 'Fonts/icon.ico' # Path to application icon

# Utility functions
def load_account_data():
    if os.path.exists(ACCOUNT_FILE):
        with open(ACCOUNT_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_account_data(data):
    with open(ACCOUNT_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def get_next_reward_time():
    now = datetime.now()
    next_wednesday_3am = now + timedelta(days=(2-now.weekday()) % 7)
    next_wednesday_3am = next_wednesday_3am.replace(hour=3, minute=0, second=0, microsecond=0)

    if now.weekday() == 2 and now.hour >= 3:
        next_wednesday_3am += timedelta(days=7)

    return next_wednesday_3am

def has_collected_reward_this_week(last_reward_time):
    if last_reward_time is None:
        return False

    last_reward_time = datetime.strptime(last_reward_time, "%Y-%m-%d %H:%M:%S")
    next_reward_time = get_next_reward_time()

    return last_reward_time >= next_reward_time - timedelta(days=7)

def time_until_next_reward():
    next_reward_time = get_next_reward_time()
    now = datetime.now()
    return next_reward_time - now

def get_player_name(steam_id):
    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={STEAM_API_KEY}&steamids={steam_id}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['response']['players'][0]['personaname']
    except (requests.exceptions.HTTPError, KeyError) as err:
        print(f"Error retrieving player nickname : {err}")
        return None

def check_rewards(steam_id):
    player_name = get_player_name(steam_id)
    account_data = load_account_data()
    last_reward_time = account_data.get(steam_id, None)

    if player_name:
        if not has_collected_reward_this_week(last_reward_time):
            result_label.config(text=f"The Steam ID account {steam_id} ({player_name}) has not yet collected its weekly care package.")
            collected = messagebox.askyesno(f"Initial creation of {player_name}", "Have you collected your weekly care package?")
            if collected:
                account_data[steam_id] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_account_data(account_data)
                result_label.config(text=f"The Steam ID account {steam_id} ({player_name}) has collected his weekly care package.")
        else:
            time_diff = time_until_next_reward()
            days, seconds = time_diff.days, time_diff.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            result_label.config(bg='black')
            result_label.config(text=f"The Steam ID account {steam_id} ({player_name}) has already collected his weekly care package this week.\n \nTime remaining until next reward : \n {days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s).")
    else:
        result_label.config(text=f"The Steam ID account {steam_id} has not yet collected his weekly care package. Impossible to retrieve the player's username.")

# GUI setup

def on_submit():
    steam_id = steam_id_entry.get()
    check_rewards(steam_id)

root = Tk()

root.title("CS2 Weekly Care Package Viewer")

# Load the background image
bg_image = Image.open(BACKGROUND_IMAGE_PATH)
bg_photo = ImageTk.PhotoImage(bg_image)

# Set the window icon
root.iconphoto(False, ImageTk.PhotoImage(file=ICON_PATH))

# Create a canvas
canvas = Canvas(root, width=bg_image.width, height=bg_image.height)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Title BOLD
canvas.create_text(265, 75, text="Enter the Steam account ID:", fill="black", font=('Verdana', 16, 'bold'))

# "Steam ID value" bar
steam_id_entry = Entry(root, width=50)
canvas.create_window(265, 130, window=steam_id_entry)


# Button "Check rewards"
submit_button = Button(root, text="Checking rewards", command=on_submit, bg='light blue', fg='black', font=('Helvetica', 12), bd=1, relief='raised', padx=10, pady=5)
canvas.create_window(265, 180, window=submit_button)

# Result after submit
result_label = Label(root, text="", wraplength=450, fg='white', font=('Calibri', 13))
canvas.create_window(265, 280, window=result_label)

#Credits
canvas.create_rectangle(100, 440, 420, 490, fill="black")
canvas.create_text(170, 460, anchor='w', text="Created and Developed by TW1X \n              4Help Discord : tw1x", fill="white", font=('Helvetica', 9, 'italic'))



root.mainloop()
