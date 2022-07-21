import time
from multiprocessing import Process
from base.compare import Compare


PROCESS = None


def start_process():
    while True:
        capture = Compare()
        capture.compare_admin_with_namespace('terminal_sessions')
        capture.compare_admin_with_namespace('environment_sessions')
        time.sleep(10)


def controller(instruction):
    message = ''
    global PROCESS
    if instruction == "start":
        if not PROCESS:
            print("Starting Process.....")
            PROCESS = Process(target=start_process)
            PROCESS.start()
            message = "Process started..."
        else:
            message = "Process already running..."
    elif instruction == "stop":
        if PROCESS:
            print("Stopping process....")
            PROCESS.kill()
            message = "Process stopped..."
            PROCESS = None
        else:
            message = "Process is not running...."
    return message
