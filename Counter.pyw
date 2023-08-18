import PySimpleGUI as sg
import json
import keyboard
import requests

CURRENT_VERSION = "v1.0.0"  # Your current app version
GITHUB_REPO_API_URL = "https://api.github.com/repos/USERNAME/REPO_NAME/releases/latest"

def main_gui():
    global settings
    try:
        with open("settings.json", "r") as settings_file:
            settings = json.load(settings_file)
    except FileNotFoundError:
        settings = {
            "win_key": "w",
            "loss_key": "l"
        }

sg.theme('DarkBrown4')

win_counter = 0
loss_counter = 0

win_action_taken = False
loss_action_taken = False

match_history = []

settings = {}

def check_for_updates():
    try:
        response = requests.get(GITHUB_REPO_API_URL)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        latest_release = response.json()
        latest_version = latest_release['tag_name']

        if latest_version > CURRENT_VERSION:
            return True, latest_version
        else:
            return False, None
    except requests.RequestException:
        return False, None

def increment_win_counter():
    global win_counter
    win_counter += 1
    match_history.insert(0, 'W')  # Add the win to the leftmost position
    while len(match_history) > 5:  # Ensure the history only keeps the last 5 matches
        match_history.pop()
    update_display()
    save_to_file()

def decrement_win_counter():
    global win_counter
    if win_counter > 0:
        win_counter -= 1
    update_display()
    save_to_file()

def increment_loss_counter():
    global loss_counter
    loss_counter += 1
    match_history.insert(0, 'L')  # Add the loss to the leftmost position
    while len(match_history) > 5:  # Ensure the history only keeps the last 5 matches
        match_history.pop()
    update_display()
    save_to_file()

def decrement_loss_counter():
    global loss_counter
    if loss_counter > 0:
        loss_counter -= 1
    update_display()
    save_to_file()

def reset_counters():
    global win_counter, loss_counter
    win_counter = 0
    loss_counter = 0
    update_display()
    save_to_file()

def update_display():
    total_games = win_counter + loss_counter
    winrate = (win_counter / total_games) * 100 if total_games != 0 else 0

    window['-WIN-VALUE-'].update(value=win_counter)
    window['-LOSS-VALUE-'].update(value=loss_counter)
    
    if window['-TOGGLE-ADVANCED-'].get():
        window['-OUTPUT-'].update(value=f"Winrate: {winrate:.2f}%")
        window['-HISTORY-'].update(value="Last 5: " + ''.join(match_history))
    else:
        window['-OUTPUT-'].update(value="")
        window['-HISTORY-'].update(value="")


def update_history(result):
    global match_history
    match_history.append(result)
    if len(match_history) > 5:
        match_history.pop(0)

def save_to_file():
    total_games = win_counter + loss_counter
    winrate = (win_counter / total_games) * 100 if total_games != 0 else 0

    with open("count.txt", "w") as file:
        file.write(f"Wins: {win_counter}\n")
        file.write(f"Losses: {loss_counter}\n")
        
        if window['-TOGGLE-ADVANCED-'].get():
            file.write(f"Winrate: {winrate:.2f}%\n")
            file.write(f"{''.join(match_history)}")
    
    window['-STATUS-'].update("Counts saved to count.txt")

def save_settings():
    with open("settings.json", "w") as settings_file:
        json.dump(settings, settings_file)

layout = [
    [sg.Text("Win-Loss Counter", font=("Helvetica", 18))],
    [
        sg.Button("+", size=(4, 1), key='-WIN-INC-'),
        sg.Button("-", size=(4, 1), key='-WIN-DEC-'),
        sg.Text("Wins:"),
        sg.Text(win_counter, size=(4, 1), key='-WIN-VALUE-')
    ],
    [
        sg.Button("+", size=(4, 1), key='-LOSS-INC-'),
        sg.Button("-", size=(4, 1), key='-LOSS-DEC-'),
        sg.Text("Losses:"),
        sg.Text(loss_counter, size=(4, 1), key='-LOSS-VALUE-')
    ],
    [sg.Button("Reset Counts"), sg.Button("Settings")],
    [sg.Button("Update Display", key='-UPDATE-DISPLAY-')],
    [sg.Checkbox('Show Advanced Stats', default=False, key='-TOGGLE-ADVANCED-')],
    [sg.Text("", size=(20, 1), key='-STATUS-', text_color='green')],
    [sg.Text("Winrate:", size=(7, 1)), sg.Text("", size=(12, 1), key='-OUTPUT-')],
    [sg.Text("Last 5:", size=(7, 1)), sg.Text("", size=(10, 1), key='-HISTORY-')],
]

window = sg.Window("Win-Loss Counter", layout, finalize=True)

while True:
    event, values = window.read(timeout=100)  # Add a small timeout to prevent GUI lockup

    # Check for key events using the keyboard library
    if keyboard.is_pressed(settings.get('win_key', 'w')) and not win_action_taken:
        increment_win_counter()
        win_action_taken = True
    elif not keyboard.is_pressed(settings.get('win_key', 'w')):
        win_action_taken = False
    elif event == '-TOGGLE-ADVANCED-':
        update_display()

    if keyboard.is_pressed(settings.get('loss_key', 'l')) and not loss_action_taken:
        increment_loss_counter()
        loss_action_taken = True
    elif not keyboard.is_pressed(settings.get('loss_key', 'l')):
        loss_action_taken = False
    elif event == '-TOGGLE-ADVANCED-':
        update_display()

    if event == sg.WIN_CLOSED:
        break
    elif event == "Check for Updates":
        update_available, new_version = check_for_updates()
        if update_available:
            sg.popup(f"A new version ({new_version}) is available on GitHub!")
        else:
            sg.popup("You have the latest version!")
    elif event == '-WIN-' and not win_action_taken:
        increment_win_counter()
        win_action_taken = True
    elif event == '-LOSS-' and not loss_action_taken:
        increment_loss_counter()
        loss_action_taken = True
    elif event == '-TOGGLE-ADVANCED-':  # Checkbox toggle event
        update_display()
    elif event == '-WIN-INC-':
        increment_win_counter()
    elif event == '-WIN-DEC-':
        decrement_win_counter()
    elif event == '-LOSS-INC-':
        increment_loss_counter()
    elif event == '-UPDATE-DISPLAY-':
        update_display()
    elif event == '-LOSS-DEC-':
        decrement_loss_counter()
    elif event == '-SAVE-':
        
        save_to_file()
    elif event == 'Settings':
        settings_layout = [
            [sg.Text("Settings", font=("Helvetica", 18))],
            [sg.Text("Win Key:"), sg.InputText(settings.get('win_key', 'w'), key='-WIN-KEY-')],
            [sg.Text("Loss Key:"), sg.InputText(settings.get('loss_key', 'l'), key='-LOSS-KEY-')],
            [sg.Button("Save Settings")]
        ]
        settings_window = sg.Window("Settings", settings_layout, finalize=True)

        while True:
            settings_event, settings_values = settings_window.read()
            if settings_event == sg.WIN_CLOSED:
                break
            elif settings_event == "Save Settings":
                settings['win_key'] = settings_values['-WIN-KEY-']
                settings['loss_key'] = settings_values['-LOSS-KEY-']
                save_settings()
                settings_window.close()
                break
    elif event == 'Reset Counts':
        reset_counters()
