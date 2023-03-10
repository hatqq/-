import requests
import time
import logging
import threading
import PySimpleGUI as sg


logging.basicConfig(level=logging.ERROR)

sg.theme('DarkGrey12') ### THEME

layout = [
    [sg.Text('Enter the message to send:', font='Arial 14')],
    [sg.InputText(key='message', font='Arial 12')],
    [sg.Button('Start', font='Arial 12', button_color=('white', '#1F2833')), sg.Button('Stop', font='Arial 12', button_color=('white', '#1F2833'))],
    [sg.Text('Status: Stopped', key='status_label', font='Arial 12', size=(20,1))],
    [sg.Text('Time until next message: N/A', key='time_label', font='Arial 12', size=(40,1))]
]

window = sg.Window('IMVU Mafias Messenger', layout, icon='imgs/Mafia.ico') ### NAME/ICON

WEBHOOK_URL = 'YOUR_WEBHOOK_URL' ### WEBHOOK
INTERVAL = 86400 ### TIME
running = False


def send_message(message):
    try:
        response = requests.post(WEBHOOK_URL, json={'content': message})
        response.raise_for_status()
    except Exception as e:
        logging.error(f'Error sending daily message: {e}')


def message_sender(message):
    global running
    time_left = INTERVAL - (time.time() % INTERVAL)
    while running:
        hours_left = int(time_left // 3600)
        minutes_left = int((time_left % 3600) // 60)
        seconds_left = int(time_left % 60)
        window['time_label'].update(f'Time until next message: {hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}')
        if time_left <= 1:
            send_message(message)
            time_left = INTERVAL
        time_left -= 1
        time.sleep(1)
    window['status_label'].update('Status: Stopped')
    window['time_label'].update('Time until next message: N/A')



while True:
    event, values = window.read(timeout=100)
    if event == sg.WINDOW_CLOSED:
        break
    if event == 'Start' and not running:
        message = values['message']
        if message:
            running = True
            window['status_label'].update('Status: Running')
            send_message(message)
            thread = threading.Thread(target=message_sender, args=(message,))
            thread.start()
        else:
            sg.popup('Please enter a message.')
    elif event == 'Start' and running:
        sg.popup('A message sending thread is already running.')
    elif event == 'Stop' and running:
        running = False
        window['status_label'].update('Status: Stopped')
        window['time_label'].update('Time until next message: N/A')

window.close()
