# main.py
import time
import os
from monitor import SystemMonitor
from gui import display
from logs import log_info

def run():
    monitor = SystemMonitor()
    log_info("System Monitor iniciado")
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            display(monitor)
            time.sleep(1.5)
    except KeyboardInterrupt:
        log_info("System Monitor finalizado")
        print("\nMonitor finalizado.")

if __name__ == "__main__":
    run()