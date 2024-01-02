import json
import socket

import Script,json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 10068))
server.listen(24)

while True:
    client = server.accept()[0]
    status = True
    data = []
    while status:
        status = client.recv(1024*1024)
        data += status
    data_json = json.loads(bytes(data).decode("utf-8"))
    if "search" == data_json["type"]:
        reply = Script.Main(data_json["data"]["character"])
        reply = json.dumps(reply,ensure_ascii=False)
        print(reply)
        client.send(str(reply).encode("utf-8"))
        client.close()
    elif "shutdown" == data_json["type"]:
        client.send('{"status":"ok"}'.encode("utf-8"))
        server.close()
        break

