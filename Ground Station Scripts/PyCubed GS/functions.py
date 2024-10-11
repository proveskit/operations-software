'''
This is the class that contains all of the functions for our CubeSat. 
We pass the cubesat object to it for the definitions and then it executes 
our will.

Authours: Michael, Nicole
'''
import time
import Big_Data
import cdh
import alarm

class functions:

    def __init__(self,cubesat):
        print("Initializing Functionalities")
        self.cubesat = cubesat
        self.debug = cubesat.debug
        self.Errorcount=0
    
    '''
    Satellite Management Functions
    '''
    def battery_heater(self):
        
        self.face_toggle("Face1",True)
        a=Big_Data.AllFaces(self.debug)
        a.Get_Thermo_Data()
        
        self.cubesat.heater_on()
        for _ in range (0,30):
           print(a.Get_Thermo_Data())
           time.sleep(1) 
        self.cubesat.heater_off()
        
        return True
    
    def current_check(self):
        return self.cubesat.current_draw

    '''
    Radio Functions
    '''  
    def send(self,msg):
        
        #This just passes the message through. Maybe add more functionality later. 
        self.cubesat.radio1.send(str(msg),keep_listening = True)
        if self.debug: print(f"Sending Packet: ",msg)

        return True
    
    def send_face_data_small(self):

        data = self.all_face_data()
        i = 0

        for face in data:
            if self.debug: print(face)
            self.cubesat.radio1.send("Face Data: " + str(i) + " " + str(face))
            i+=1
    
    def listen(self):

        #This just passes the message through. Maybe add more functionality later. 
        received = self.cubesat.radio1.receive()
        if self.debug: print(f"Recieved Packet: ",received)
        time.sleep(5)
        if received is not None:
            cdh.message_handler(self.cubesat, received)

        return received
    
    '''
    Big_Data Face Functions
    '''  
    def face_toggle(self,face,state):
        
        on_off = not state 
        
        if face == "Face0": self.cubesat.zPosFet.value = on_off      
        elif face == "Face1": self.cubesat.zNegFet.value = on_off
        elif face == "Face2": self.cubesat.yPosFet.value = on_off      
        elif face == "Face3": self.cubesat.xNegFet.value = on_off           
        elif face == "Face4": self.cubesat.xPosFet.value = on_off          
        elif face == "Face5": self.cubesat.yNegFet.value = on_off

    '''
    def face_data(self,face,data_type):
        
        if face == "Face0": 
            self.face_toggle(face,True)
            
        elif face == "Face1": self.cubesat.zNegFet.value = on_off
        elif face == "Face2": self.cubesat.yPosFet.value = on_off      
        elif face == "Face3": self.cubesat.xNegFet.value = on_off           
        elif face == "Face4": self.cubesat.xPosFet.value = on_off          
        elif face == "Face5": self.cubesat.yNegFet.value = on_off

        return data
    '''
    
    def all_face_data(self):
        
        self.cubesat.all_faces_on()
        a = Big_Data.AllFaces(self.debug)
        
        data = a.Face_Test_All()
        
        del a
        self.cubesat.all_faces_off()
        
        return data
    
    def get_imu_data(self):
        
        self.cubesat.all_faces_on()
        a = Big_Data.AllFaces(self.debug)
        
        data = a.Get_IMU_Data()
        
        del a
        self.cubesat.all_faces_off()
        
        return data
    
    '''
    Spresense Functions
    '''  
    #Function to take a 480p picture from the Spresense
    def get_picture(self):
        
        if self.debug: print("Initiating Spresense")
        
        #Activate the Spresense and wait for the UART to be ready
        self.cubesat.Spresense_on()
        time.sleep(1)
        self.cubesat.uart.reset_input_buffer()
        
        #Initialize helper variables
        count=0
        data_string=""
        self.packetstring=[]
        self.image_packets=0
        self.cubesat.uart.timeout=2
        self.cubesat.uart.write(bytearray("yes"))

        while count<7:
            #Reading the data from the UART buffer
            data = self.cubesat.uart.read(200)  # read 100 hex bytes
            self.cubesat.uart.reset_input_buffer()

            try:
                while data is not None:
                    #Blocking while loop to continue reading the data until no new data is sent
                    if self.debug: print("Packet " + str(self.image_packets+1) + ":")
                    count=0
                    self.image_packets+=1
                    
                    # convert bytearray to string
                    data_string = ''.join([chr(b) for b in data])
                    self.packetstring.append(data_string)
                    if self.debug: print(data_string, end="")
                    
                    #Read new set of data
                    data = self.cubesat.uart.read(200)  # read 100 hex bytes
                    self.cubesat.uart.reset_input_buffer()
                    
                    #Ack Message
                    if self.debug: print("\nI wrote back")
                    self.cubesat.uart.write(bytearray("True"))

            except Exception as e:
                print('Picture receive error:',e)

            if self.debug: print("missed packet")
            self.cubesat.uart.write(bytearray("True"))
            time.sleep(1)
            count+=3 #While loop escape in case of no data 

        self.cubesat.uart.write(bytearray("Done"))

        self.cubesat.Spresense_off()

        return self.packetstring

    '''
    Logging Functions
    '''  
    def log_face_data(self,data):
        
        if self.debug: print("Logging Face Data")
        try:
                self.cubesat.Face_log(data)
        except:
            try:
                self.cubesat.new_file(self.cubesat.Facelogfile)
            except Exception as e:
                print('SD error:',e)
        
    def log_error_data(self,data):
        
        if self.debug: print("Logging Error Data")
        try:
                self.cubesat.log(data)
        except:
            try:
                self.cubesat.new_file(self.cubesat.logfile)
            except Exception as e:
                print('SD error:',e)
    
    def log_image_data(self,data):
        
        try:
            if self.debug: print("Here is the image")
            if self.debug: print(*data, sep='')
            
            try:
                    self.cubesat.Image_log(data)
            except:
                try:
                    self.cubesat.new_file(self.cubesat.Imagelogfile)
                except Exception as e:
                    print('SD error:',e)
        except Exception as e:
            print('Print error:',e)
    
    '''
    Misc Functions
    '''  
    def torque(self):
        

        return True
    
    def Short_Hybernate(self):
        if self.debug: print("Short Hybernation Coming UP")
        #all should be off from cubesat powermode
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 10)#change to 2 min when not testing
        # Exit the program, and then deep sleep until the alarm wakes us.
        alarm.exit_and_deep_sleep_until_alarms(time_alarm)
        return True
    
    def Long_Hybernate(self):
        #all should be off from cubesat powermode
        time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 600)
        # Exit the program, and then deep sleep until the alarm wakes us.
        alarm.exit_and_deep_sleep_until_alarms(time_alarm)
        return True
    
    '''
    Holding Area
    '''
    #Function to send Spresense and Face data over radio:
    def Data_Transmit(self, type, data):
        if type == "Spresense":
            count=1
            for i in data:
                if self.debug: print(f"Sending packet ", count, "/", self.image_packets, ": ", i)
                self.radio1.send(i)
                time.sleep(1)
                count+=1
        elif type == "Face":
            count=1
            for i in data:
                if self.debug: print(f"Sending face ", count, "/", 6, ": ", i)
                self.radio1.send(str(i)) #Note this is data ineffiecient because of the extra ASCII formatting characters
                time.sleep(1)
                count+=1
        elif type == "Error":
            count=1
            for i in data:
                if self.debug: print(f"Sending Error ", self.Errorcount, "/", 6, ": ", i)
                self.radio1.send(str(i)) #Note this is data ineffiecient because of the extra ASCII formatting characters
                time.sleep(1)
                count+=1
        else:
            if self.debug: print(f"No type with name: ", type, " nothing transmitted")