from pycubed import cubesat as c
import time

c.radio1.spreading_factor=8
c.radio1.node=0xfa
c.radio1.destination=0xfb
c.radio1.receive_timeout=10
c.radio1.enable_crc=True

cmd = b'Heya'+ b'p\xba\xb8C' + b'\x96\xa2' + 'c.radio1.send(str(c.hardware))'
cmd1 = b'Heya'+ b'p\xba\xb8C' + b'\x96\xa2' + b'f.send_face()'
while True:
    msg = c.radio1.receive()

    print(f"Message Received {msg}")

    if msg == b'packet1/1: KN6NAQ Hello I am Yearling! IHBPFJASTMNE! KN6NAQ':
        print(f"Receieved Command Window")

        for _ in range(0,5):
            print(f"Sending CMD: {cmd}")
            c.radio1.send(cmd,keep_listening = True)
            msg = c.radio1.receive()
            while msg is not None:
                print(f"Message Received {msg}")
                time.sleep(1)
                msg = c.radio1.receive()


