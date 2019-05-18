import asyncio
import pathlib
import ssl
import websockets
from time import sleep


async def run(websocket, path):
    async def Recive():
        print('----------------------')
        received = None
        try:
            received = await websocket.recv()
        except Exception as error:
            print("Error while receiving: " + str(error))
            await Recive()

        print("Client say: ")
        print(received)
        await Send(received)


    async def Send(received):
        print('----------------------')
        try:
            await websocket.send(bytes(received.upper(), "utf-8"))
        except Exception as error:
            print("Error while sending: " + str(error))
            await websocket.send(bytes('NOP', "utf-8"))
            sleep(60)
            await Send(received)

        await file()


    async def file():
        with open('result.txt', 'w') as file:
            while True:
                try:
                    datachunk = (str(await websocket.recv(), "utf-8"))
                    file.write(datachunk + '\n')
                except Exception:
                    file.close()
                    break
        file.close()
        print("'result.txt' has created")

    await Recive()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(pathlib.Path(__file__).with_name('localhost.pem'))

server = websockets.serve(run, 'localhost', 8765, ssl=ssl_context)

asyncio.get_event_loop().run_until_complete(server)
print("Server is running..")

asyncio.get_event_loop().run_forever()