'''
Author: vvthai
Description: Run websocket by python: python index.py
'''
import json
import asyncio
import websockets
import transformers
from bs4 import BeautifulSoup
from datasets import load_dataset
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification, TextClassificationPipeline

base_model_name = "valurank/finetuned-distilbert-adult-content-detection"
tokenizer = AutoTokenizer.from_pretrained(base_model_name)
model = transformers.AutoModelForSequenceClassification.from_pretrained(base_model_name, id2label={0: 'safe', 1: 'not safe'})
pipe = TextClassificationPipeline(model=model, tokenizer=tokenizer, return_all_scores = True)

def is_safe(inpt_text: str):
    global pipe
    outp_rate = pipe(inpt_text)
    return True if max(outp_rate[0], key=lambda x: x['score'])['label'] == 'safe' else False

def extract_adult_pid(html):
    soup = BeautifulSoup(html, 'html.parser')
    pid = []
    for p_tag in soup.find_all('p', attrs={'data-p-id': True}):
        # Check if the <p> tag contains any <span> tags
        if p_tag.find('span'):
            # Remove text from nested <span> tags
            for span_tag in p_tag.find_all('span'):
                span_tag.extract()
        # Extract the text from the <p> tag and evaluate it
        p_text = p_tag.get_text(strip=True).rstrip('\n')
        # Get list of <p> data-p-id
        if not is_safe(p_text):
            pid.append(p_tag.get('data-p-id'))
    return json.dumps(pid)

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
