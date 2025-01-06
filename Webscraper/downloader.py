from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import base64
import re
import xlsxwriter
from enum import Enum

#############################################
#                                           #
#   RUN COMMAND: python downloader.py       #
#                                           #
#############################################
#happy data fetching! -alex

# Opening chrome and bypassing javascript requirement
chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)

URL = "https://tinygs.com/satellite/PROVES"

driver.get(URL)
time.sleep(1)
#finding packets which are clickable v-cards in tinygs
packets = driver.find_elements(By.CLASS_NAME, "v-card--link")

#creating an excel file
workbook = xlsxwriter.Workbook('ProvesDownlink2.xlsx')
worksheet = workbook.add_worksheet()
row = 10 #start
col = 0

master_recent_packet = [None] * 7
#beacon_packet = None
#soh1_packet = None
#soh2_packet = None
#detumble_packet = None
#imu_packet = None
#face_packet = None
#joke_packet = None

class packetType(Enum):
    BEACON = 0
    SOH1 = 1
    SOH2 = 2
    DETUMBLE = 3
    IMU = 4
    FACE = 5
    JOKE = 6

for p in packets:
    try:
        packet_link = p.get_attribute("href")
        #print(packet_link)
        
        packet_driver = webdriver.Chrome(options=chrome_options)
        packet_driver.get(packet_link)
        time.sleep(5)
        
        #Get Date
        received_string = re.search(r'Received on: .*?<\/div>', packet_driver.page_source)
        split_list = re.split(r'(: |<)', received_string.group())
        date = split_list[2]
        #print(date)


        #Geting Data
        download_button = packet_driver.find_element(By.CLASS_NAME, "download-btn")
        href = download_button.get_attribute("href")
        if href is not None:
            #removes data:application/octet-stream section, gets the full base_64 and removes the first byte
            base_64_message = href.split(",")[1][4::]
            utf8_string = base64.b64decode(base_64_message).decode("utf-8")

            first_word = utf8_string.split(' ', 2)[1]
            
            template = re.compile(r'NoSearch')
            packet_type = None
            result_list = []

            #Template matching
            if first_word == "Hello":           #beacon type
                #print("BEACON")
                packet_type = packetType.BEACON
                #print(utf8_string)
                template = re.compile(r'KN6NAT Hello I am Yearling\^2! I am in: (.*) power mode. V_Batt = (.*)V\. IHBPFJASTMNE! KN6NAT')
            elif first_word == "Yearling^2":      #state of health 1/2
                #print("SOH1")
                packet_type = packetType.SOH1
                template = re.compile(r"KN6NAT Yearling\^2 State of Health 1/2\['PM:(.*)', 'VB:(.*)', 'ID:(.*)', 'VS:(.*)', 'UT:(.*)', 'BN:(.*)', 'MT:(.*)', 'RT:(.*)', 'AT:(.*)', 'BT:(.*)', 'AB:(.*)', 'BO:(.*)', 'FK:(.*)'\]KN6NAT")
            elif first_word == "YSOH":          #state of health 2/2
                #print("SOH2")
                packet_type = packetType.SOH2
                template = re.compile(r"KN6NAT YSOH 2/2\{'FLD': (.*), 'Face4': (.*), 'IMU': (.*), 'Radio1': (.*), 'Neopixel': (.*), 'Face0': (.*), 'Face1': (.*), 'Face2': (.*), 'Face3': (.*), 'SDcard': (.*), 'PWR': (.*), 'WDT': (.*), 'LiDAR': (.*)\}KN6NAT")
            elif first_word == "Detumbling!":   #detumble
                #print("DETUMBLE")
                packet_type = packetType.DETUMBLE
                template = re.compile(r"KN6NAT Detumbling! Gyro, Mag: \[\((.*), (.*), (.*)\), \((.*), (.*), (.*)\)\] KN6NAT")
            elif first_word[0] == "[":          #IMU
                #print("IMU")
                packet_type = packetType.IMU
                template = re.compile(r"KN6NAT \[\((.*), (.*), (.*)\), \((.*), (.*), (.*)\), \((.*), (.*), (.*)\)\] KN6NAT")
            elif first_word == "Y-:":          #Face Data
                #print("FACE")
                packet_type = packetType.FACE
                template = re.compile(r"KN6NAT Y-: \[(.*), (.*)\] Y\+: \[(.*), (.*)\] X-: \[(.*), (.*)\] X\+: \[(.*), (.*)\]  Z-: \[(.*), (.*), \((.*), (.*), (.*)\)\] KN6NAT")
            else:                               #Joke LIKELY
                #print("JOKE")
                packet_type = packetType.JOKE
                template = re.compile(r"KN6NAT (.*) KN6NAT")
            
            #print(utf8_string)
            data = template.findall(utf8_string)
            
            #print(utf8_string)

            #prevent tuple areas (and also don't make jokes funky)
            if type(data[0]) is tuple:
                data = data[0]

            result_list.append(date)
            result_list.append(packet_type.name)
            for item in data:
                result_list.append(item)

            
            print(result_list)
            
            #save to excel
            for item in result_list:
                worksheet.write(row, col, item)
                col += 1

            #update most recent values
            if master_recent_packet[packet_type.value] is None:
                master_recent_packet[packet_type.value] = result_list

        pass
    except Exception as e:
        print("i bruhed out: ", e)

    col = 0
    row += 1

row = 0
for i in range(0, len(master_recent_packet)):
    packet_list = master_recent_packet[i]
    for item in packet_list:
        worksheet.write(row, col, item)
        col += 1
    col = 0
    row += 1


#saving excel file
workbook.close()

#print(packets)
