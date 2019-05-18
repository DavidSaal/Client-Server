import asyncio
import pathlib
import ssl
import websockets
from time import sleep

import psutil
from ctypes import *
from ctypes.wintypes import *


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.load_verify_locations(
    pathlib.Path(__file__).with_name('localhost.pem'))


async def hello():
    # Connect to server
    async with websockets.connect('wss://localhost:8765', ssl=ssl_context) as websocket:
        print("\nConnected to server..")

        async def read_process_memory(processes, received):
            OpenProcess = windll.kernel32.OpenProcess
            ReadProcessMemory = windll.kernel32.ReadProcessMemory
            CloseHandle = windll.kernel32.CloseHandle

            PROCESS_ALL_ACCESS = 0x1F0FFF
            address = hex(id(ctypes.create_string_buffer((received))))

            buffer = c_char_p(received)
            bufferSize = len(buffer.value)
            bytesRead = c_ulong(0)

            for name,pid in processes.items():
                processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
                if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
                    found = (name + ': ' + str(pid))
                    print("Found:", found)
                    try:
                        await websocket.send(bytes(found, "utf-8"))
                    except Exception as error:
                        print("Error while sending: " + str(error))

                CloseHandle(processHandle)


        async def Send(data):
            # Send data to server
            print("\nAsk for a String..")
            try:
                await websocket.send(data)
            except Exception as error:
                print("Error while sending: " + str(error))
                await Send(data)
            print('----------------------')
            await Recive()


        async def Recive():
            received = ''
            # Receive data from the server and shut down
            try:
                received = await websocket.recv()
            except Exception as error:
                print("Error while receiving: " + str(error))
                await Recive()
            if received is 'NOP':
                sleep(60)
                await Recive()
            else:
                print("\nSent:     {}".format(data))
                print("Received: {}".format("".join(filter(lambda x: x.isupper(), str(received)))))
                print('----------------------')
                print('\n## Check String in all processes memory..')

                processes = {}
                for proc in psutil.process_iter(attrs=['name', 'pid']):
                    try:
                        processes[proc.info['name']] = proc.info['pid']
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        pass
                await read_process_memory(processes, received)


        data = "".join("string")
        await Send(data)


asyncio.get_event_loop().run_until_complete(hello())