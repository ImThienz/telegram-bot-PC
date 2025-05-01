import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import subprocess
import os
import logging
import time

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Setup logging
logging.basicConfig(
    filename=os.path.join(SCRIPT_DIR, 'bot_service.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class PCBotService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PCBotService2"
    _svc_display_name_ = "PC Control Bot Service 2"
    _svc_description_ = "Telegram bot service for controlling PC"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True
        self.process = None
        self.bot_script = os.path.join(SCRIPT_DIR, "PC-bot.py")
        
        # Verify bot script exists
        if not os.path.exists(self.bot_script):
            logging.error(f"Bot script not found at: {self.bot_script}")
            raise FileNotFoundError(f"Bot script not found at: {self.bot_script}")

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        if self.process:
            self.process.terminate()
            logging.info("Bot process terminated")

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        logging.info("Service started")
        self.main()

    def main(self):
        while self.is_alive:
            try:
                if not self.process or self.process.poll() is not None:
                    logging.info("Starting bot process")
                    # Change to script directory before starting bot
                    os.chdir(SCRIPT_DIR)
                    self.process = subprocess.Popen(
                        ["python", self.bot_script],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=SCRIPT_DIR  # Set working directory
                    )
                    logging.info("Bot process started")
                
                # Check if process is still running
                if self.process.poll() is not None:
                    logging.error(f"Bot process died with return code: {self.process.returncode}")
                    stdout, stderr = self.process.communicate()
                    logging.error(f"Bot stdout: {stdout}")
                    logging.error(f"Bot stderr: {stderr}")
                
                # Wait for stop event or 5 seconds
                win32event.WaitForSingleObject(self.hWaitStop, 5000)
                
            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(5)  # Prevent tight loop on error

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(PCBotService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(PCBotService) 