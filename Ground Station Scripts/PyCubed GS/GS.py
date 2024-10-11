import board
import busio
import digitalio
import time
import adafruit_rfm9x


class Ground:
    def __init__(self):
        spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

        cs = digitalio.DigitalInOut(board.D10)
        reset = digitalio.DigitalInOut(board.D11)

        self.rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 437.4)

        self.rfm9x.spreading_factor=8
        self.rfm9x.node=0xfa
        self.rfm9x.destination=0xfb
        self.rfm9x.receive_timeout=15
        self.rfm9x.enable_crc=True
        self.secret = b'\x59\x4e\x45\x3f'
        self.cmd1 = b'Heya'+ self.secret + b'\x96\xa2' + 'c.radio1.send(str(c.hardware));c.all_faces_off();c.all_faces_on()'
        self.cmd = b'Heya'+ self.secret + b'\x96\xa2' + b'f.send_face()'
        self.msg_string=""
        self.packetstring=[]

    def send_cmd(self,cmd,pick):
        check_hardware = b'Heya'+ self.secret + b'\x96\xa2' + 'c.radio1.send(str(c.hardware))'
        face_data = b'Heya'+ self.secret + b'\x96\xa2' + b'f.send_face()'
        get_picture = b'Heya'+ self.secret + b'\x96\xa2' + b'f.get_picture()'
        get_image = b'Heya'+ self.secret + b'\x96\xa2' + b'f.send_image()'
        get_and_send = b'Heya'+ self.secret + b'\x96\xa2' + b'f.get_picture();f.send_image()'
        if cmd is not "None":
            cmd = b'Heya'+ self.secret + b'\x96\xa2' + cmd
        else:
            if pick == 0:
                cmd = face_data
            elif pick == 1:
                cmd = get_picture
            elif pick == 2:
                cmd = get_image
            elif pick == 3:
                cmd = check_hardware
            elif pick == 4:
                cmd = get_and_send
        
        while True:
            msg = self.rfm9x.receive()

            print(f"Message Received {msg}")
            if msg is not None:
                if b'KN6NAQ Hello I am Yearling!' in msg:
                    print(f"Receieved Command Window")

                    time.sleep(2)
                    
                    print(f"Sending CMD: {cmd}")
                    self.rfm9x.send(cmd,keep_listening = True)
                    if pick==4:
                        while True:
                            self.receive()
                    else:
                        self.receive()
                        
                        
    def main(self):
        while True:
            self.receive()  
                
    def receive(self):
        msg = self.rfm9x.receive()
        self.packetstring=[]
        count=0

        if msg is not None: 
            self.msg_string = ''.join([chr(b) for b in msg])
            print(f"Message Received {self.msg_string}")
            self.packetstring.append(self.msg_string[13:])
            print(self.msg_string[13:])
        else: self.msg_string=""
        if self.msg_string[:-6]=="KN6NAQ":
            for _ in range(0,2):
                print(f"Sending CMD: {self.cmd}")
                self.rfm9x.send(self.cmd,keep_listening = True)
                msg = self.rfm9x.receive()
                while msg is not None:
                    self.msg_string = ''.join([chr(b) for b in msg])
                    print("Going to iterate for ", self.msg_string[8]," times!")
                    for _ in range(int(self.msg_string[8])):
                        self.rfm9x.send("True",keep_listening=True)
                        if msg is not None:
                            print(self.msg_string)
                        time.sleep(.5)
                        msg=self.rfm9x.receive()
                        if msg is not None:
                            self.msg_string = ''.join([chr(b) for b in msg])
                        else:
                            break
                    #print(f"Message Received {msg}")
                    time.sleep(1)
                    msg = self.rfm9x.receive()
        elif self.msg_string[0:6] == "packet":
            self.rfm9x.send("True",keep_listening=True)
            print("going to iterate for ", self.msg_string[8:11], " cycles")

            if "6:" in self.msg_string:
                self.msg_string.replace("6:","6 ")
            print(self.msg_string[8:11])
            
            for a in range(int(self.msg_string[8:11])):
                msg = self.rfm9x.receive()
                if msg is not None: self.msg_string = ''.join([chr(b) for b in msg])
                else:
                    count=0
                    while count < 5:
                        self.rfm9x.send("True",keep_listening=True)
                        msg = self.rfm9x.receive()
                        if msg is not None: 
                            self.msg_string = ''.join([chr(b) for b in msg])
                            break
                        count+=1
                if count == 5:
                    break
                print(f"Message Received {self.msg_string}")
                if a >= 100:
                    print(self.msg_string[13+2:])
                    self.packetstring.append(self.msg_string[13+2:])
                elif a >= 10:
                    print(self.msg_string[13+1:])
                    self.packetstring.append(self.msg_string[13+1:])
                else:
                    print(self.msg_string[13:])
                    self.packetstring.append(self.msg_string[13:])

                self.rfm9x.send("True",keep_listening=True)

        print(*self.packetstring,sep='')


        '''if msg == b'packet1/1: KN6NAQ Hello I am Yearling! IHBPFJASTMNE! KN6NAQ':
                print(f"Receieved Command Window")
                rfm9x.send("True",keep_listening = True)
                time.sleep(.5)
                for _ in range(0,2):
                    print(f"Sending CMD: {cmd}")
                    rfm9x.send(cmd,keep_listening = True)
                    msg = rfm9x.receive()
                    while msg is not None:
                        msg_string = ''.join([chr(b) for b in msg])
                        print("Goiing to iterate for ", msg_string[8]," times!")
                        for _ in range(int(msg_string[8])):
                            rfm9x.send("True",keep_listening=True)
                            if msg is not None:
                                print(msg_string)
                            time.sleep(.5)
                            msg=rfm9x.receive()
                            if msg is not None:
                                msg_string = ''.join([chr(b) for b in msg])
                            else:
                                break
                        #print(f"Message Received {msg}")
                        time.sleep(1)
                        msg = rfm9x.receive()
        '''

g = Ground()
