'''


I will show how to use twilio whatsapp API  in order to execute commands on your machine or your Arduino board

you will need to do the following in order the code below to work:

1-create an account in www.twilio.com/referral/Xy9NoB
2-after creating the account , set theses variables based on the information provided in your dashboard.
account_sid = 'Your Account SID'
auth_token = 'Your Token'
sender = 'whatsapp:Provided Number'
3-install twilio api  and for more info go to this link https://www.twilio.com/docs/libraries/python
pip install twilio
4-install pyfirmata in your python project
pip install pyfirmata
5- install arduino  IDE on your machine from this link https://www.arduino.cc/en/Main/Software
6- upload firmata standard on your arduino board.

Now you are ready to test the code

'''

from functools import partial
from twilio.rest import Client
import datetime,time
import os
import re
from pyfirmata import Arduino,util
import serial.tools.list_ports

#Twilio API Config
account_sid = 'AC206d1e54cxxxxxd532a8125595101'
auth_token = 'c43b9d3a8b61086a1xxxxx1dcb755455'
sender = 'whatsapp:+14153522386'
client = Client(account_sid, auth_token)

ports = list(serial.tools.list_ports.comports())
ArduinoisConnected = False
if len(ports) > 0:
    port = str(ports[0]).split(' ')[0]
    board = Arduino(port)
    if board:
        ArduinoisConnected=True
    else:
         ArduinoisConnected=False
else:
    ArduinoisConnected = False

# return instructions when user enters wrong keywords
def help():
    help = """
    Help Menu (Beta Version): \n
       1- ping www.example.xxx or www.example.xxx.xx or example.xxx or example.xxx.xx \n
       2- switch on \n
       3- switch off \n
    """
    return help

# read the last incoming message
def read_messages():
    try:
        d = datetime.datetime.today()
        year = d.year
        month = d.month
        day = d.day
        hours = d.hour
        minutes = d.minute
        seconds = d.second
        messages = client.messages.list(
            limit=1
        )
        for record in messages:
            if record.direction == "inbound":
                print(record.body)
                switcher(record.body, record.from_)
    except:
       print("something went wrong")

#replay on the last incoming message
def create_message(msg,to):
    try:
        message = client.messages.create(
            from_=sender,
            body=msg,
            to=to
        )
        print('message was sent successfully' + message.sid)
    except:
        print("something  went wrong")

#switch LED on and off on arduino board pin 13
def switch_on_off(msg):
    if(ArduinoisConnected):
        if len(msg) > 0:
            if msg == "on":
                board.digital[13].write(1)
                return "LED Light is on"
            elif msg == "off":
                board.digital[13].write(0)
                return "LED Light is off"
            else:
                return help()
        else:
            return help()
    return "Arduino is not connected"

#test sites using ping command
def ping_function(msg):
    if len(msg) > 0:
        res = re.fullmatch(r"^([a-zA-Z]{3}).?([a-zA-Z]+).([a-zA-Z]{3}).?([a-zA-Z]{2})?$",msg)
        if res is not None:
            os.system('ping ' + msg + ' > result.txt')
            result = open("result.txt", "r")
            return result.read()
        else:
            return help()
    else:
        return help()


#specific function will be executed if the keyword is matched otherwise help menu will be shown
def switcher(msg,to):
    if len(msg.split(' ')) > 1:
        cmd = msg.split(' ')[0]
        cmd_request = msg.split(' ')[1]
    else:
        cmd = msg
        cmd_request = ''
    switch = {
        "ping": partial(ping_function,cmd_request),
        "switch": partial(switch_on_off,cmd_request),
        "help": help
    }

    func = switch.get(cmd, help)
    create_message(func(),to)


#read message every 5 seconds
while True:
    read_messages()
    time.sleep(5)
