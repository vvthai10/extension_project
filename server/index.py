'''
Author: vvthai
Description: Run websocket by python: python index.py
'''
import json
import asyncio
import websockets
from bs4 import BeautifulSoup
from AI import find_content_id, contain_a_z

            

def extract_adult_pid(html):
    soup = BeautifulSoup(html, 'html.parser')    
    tag_list = soup.find_all('p', attrs={'data-p-id': True})
    text_list = []
    id_list = []
    for p_tag in tag_list:        
        # Check if the <p> tag contains any <span> tags
        if p_tag.find('span'):
            # Remove text from nested <span> tags
            for span_tag in p_tag.find_all('span'):
                span_tag.extract()
        # Extract the text from the <p> tag and evaluate it
        p_text = p_tag.get_text(strip=True).rstrip('\n')
        # check if p_text have any char from a to z
        if not contain_a_z(p_text):
            continue
        text_list.append(p_text)
        id_list.append(p_tag.get('data-p-id'))
    new_tag_text, tag_id = find_content_id(text_list, id_list, 'sexual')   
    # TODO: send new_text, id to server
    return json.dumps((tag_id, new_tag_text))

async def handle_connection(websocket, path):
    print("New client connected!")
    await websocket.send("Hello from server!")

    try:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            

            print("Received message from client:", data['tabId'])

            # Xử lý dữ liệu nhận được từ client
            json_data = extract_adult_pid(data['html'])
            # Gửi dữ liệu từ server tới client
            # response = "Hello from server!"
            data = {
                "tabId": data['tabId'],
                "message": json_data
            }                        
            await websocket.send(json.dumps(data))
            
    except websockets.exceptions.ConnectionClosedOK:
        print("Client has disconnected")

start_server = websockets.serve(handle_connection, "localhost", 8082)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()