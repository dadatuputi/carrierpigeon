import logging
import time
from signal import pause
import argparse
from fysom import Fysom
from gpiozero import Button, PWMLED, RGBLED
from carrierpigeon import mail, audio, log_format

logger = logging.getLogger(__name__)

state = None

def record_audio():
    global thread_record
        
def stop_record():
    global thread_record
    print("stopping: {}".format(thread_record))
    if thread_record:
        thread_record.stop.set()
        thread_record.join()

# state = rec
def onrec(e):
    
    # Record until release
    e.threads['rec'].rec()
    if buttons['red'].is_held():
        buttons['red'].wait_for_release()
        e.thread.stop()
        # get audio file location from rec thread
        recording = None
        e.fsm.play_rec(recording, 'threads' = e.threads, 'buttons' = e.buttons, 'leds' = e.leds)
    else:
        e.thread.stop()
        e.fsm.rec_cancel()

# state = play_rec
def onplay_rec(e):
    pass

# state = send_msg
def onsend_msg(e):
    pass

# state = play_msg
def onplay_msg(e):
    pass

# state = notify
def onnotify(e):
    pass

# state = nav
def onnav(e):
    pass


def main():
    ## START

    # Set logging verbosity from arguments
    parser = argparse.ArgumentParser(description='E-mail based audio messenger for kids and their loved ones.')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Set logging level to console')
    args = parser.parse_args()
   
    # Parse arguments
    if args.verbose > 0:
        # Set up console logger at INFO level
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)

        # -vv or greater debugs at DEBUG level
        if args.verbose > 1:
            console_handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)

        root_logger.info("Console logging set to {}".format(logging.getLevelName(root_logger.getEffectiveLevel())))

    ## INITIALIZATION

    # Set up Finite State Machine using Fysom: https://github.com/mriehl/fysom
    # FSM is defined at https://www.lucidchart.com/invitations/accept/af5b86f9-d5ef-42a6-b399-e74c64d91fe2
    fsm = Fysom({
        'initial': {'state': 'nav', 'event': 'init', 'defer': True},
        'events': [
            {'name': 'new_msg', 'src': 'nav', 'dst': 'notify'},
            {'name': 'new_msg', 'src': 'play_msg', 'dst': 'play_msg'},


            {'name': 'b_mode_press', 'src': 'nav', 'dst': 'nav'},
            {'name': 'b_mode_press', 'src': 'notify', 'dst': 'play_msg'},

            {'name': 'b_left_press', 'src': 'play_rec', 'dst': 'nav'},
            {'name': 'b_left_press', 'src': ['nav', 'notify'], 'dst': 'play_msg'},

            {'name': 'b_right_press', 'src': 'play_rec', 'dst': 'nav'},
            {'name': 'b_right_press', 'src': ['nav', 'notify'], 'dst': 'play_msg'},

            {'name': 'b_main_press', 'src': 'play_rec', 'dst': 'send_msg'},
            {'name': 'b_main_press', 'src': 'notify', 'dst': 'play_msg'},
            {'name': 'b_main_hold', 'src': ['nav', 'play_rec'], 'dst': 'rec'},
            {'name': 'b_main_release', 'src': 'rec', 'dst': 'play_rec'},


            {'name': 'play_complete', 'src': 'play_msg', 'dst': 'nav'},
            {'name': 'timeout', 'src': 'play_rec', 'dst': 'nav'},
            {'name': 'send_complete', 'src': 'send_msg', 'dst': 'nav'},
            {'name': 'rec_cancel', 'src': 'rec', 'dst': 'nav'}
            ],
        'callbacks': {
            'onnav': onnav,
            'onnotify': onnotify,
            'onplay_msg': onplay_msg,
            'onsend_msg': onsend_msg,
            'onplay_rec': onplay_rec,
            'onrec': onrec
            }
    })

    # Set up threads
    # Mail Thread
    thread_mail = mail.IMAPThread()
    thread_mail.run()

    # Record Thread
    thread_rec = audio.RecordThread()
    thread_rec.start()

    # Buttons - these fire most of the events
    # Main button
    b_main = Button(1, bounce_time=.1) 
    b_main.when_pressed = fsm.b_main_press
    b_main.when_held = fsm.b_main_hold
    b_main.when_released = fsm.b_main_release
    # Mode button
    b_mode = Button(2, bounce_time=.1)
    b_mode.when_pressed = fsm.b_mode_press
    # Left button
    b_left = Button(3, bounce_time=.1)
    b_left.when_pressed = fsm.b_left_press
    # Right button
    b_right = Button(4, bounce_time=.1)
    b_right.when_pressed = fsm.b_right_press

    buttons = {
            'main': b_main,
            'mode': b_mode,
            'left': b_left, 
            'right': b_right} 

    # LEDs
    leds = {
            'main': PWMLED(5),
            'mode': RGBLED(6,7,8),
            'left': RGBLED(9,10,11),
            'right': RGBLED(12,13,14)}

    # This dict will be available to all states to keep track of threads, buttons, leds, and the fsm
    global state
    state = {
        'threads': {
            'mail': thread_imap,
            'rec': thread_rec},
        'buttons' = buttons,
        'leds' = leds,
        'fsm': fsm}

    fsm.init()

    pause()

if __name__ == "__main__":
    main()
