'''
Author: vvthai
Description: Run websocket by python: python index.py
'''
import json
import asyncio
import websockets
import transformers
from bs4 import BeautifulSoup
import pickle as pkl


basic_labels = ['romantic love' ,'daily talk', 'complaint', 'sarcasm', 'humor', 'anger', 'sadness', 'joy', 'fear', 'surprise', 'disgust', 'curiosity', 'other']
# pipe = transformers.pipeline("zero-shot-classification", model="facebook/bart-large-mnli", topk=None)
pipe = None


# define a function to standardize text
def standardize_text(text:str):
    # only keep characters from a-z and A-Z and space
    for char in text:
        if not char.isalpha():
            text = text.replace(char, '')        
    return text
    

# define a function to parse paragraph into sentences
def parse_paragraph(paragraph:str):          
    paragraph = standardize_text(paragraph)  
    sentences = paragraph.split('.')    
    # remove sentences without any alphabetic characters
    for index in range(len(sentences)):        
        if not any(ch.isalpha() for ch in sentences[index]):
            sentences.pop(index)
            continue
        # remove abundant spaces
        for ch in ['  ', '   ', '    ', '     ', '      ']:
            sentences[index] = sentences[index].replace(ch, ' ')
        # remove spaces at the beginning of sentences or end of sentences
        if sentences[index][0] == ' ':
            sentences[index] = sentences[index][1:]
        if sentences[index][-1] == ' ':
            sentences[index] = sentences[index][:-1]
    return sentences

def match_label(inpt_text: str, target_label = "sexual"):
    # check if input text have any char from a to z
    def contain_a_z(text: str):
        for char in text:        
            int_rep = ord(char.lower())
            if int_rep in range(97, 123):
                return True
        return False
    
    #handle input text
    if not contain_a_z(inpt_text):
        return False
    global pipe, basic_labels   
    # create a list of labels (target label + basic labels), more labels is better for classification    
    labels = basic_labels.copy()
    if target_label not in labels:
        labels.append(target_label)    
    # parse and standardize paragraph into sentences
    sentences = parse_paragraph(inpt_text)
    # check if any sentence match with target label 
    # p/s: will use divide and conquer algorithm to reduce time complexity in the future
    for sentence in sentences:
        output = pipe(sentence, labels, multi_label=True)        
        if output['labels'][0] == target_label:
            return True
    return False

def extract_adult_pid(html):
    soup = BeautifulSoup(html, 'html.parser')
    response = [] # response is a list of <p> data-p-id and text 
    show_progress = True # show progress of extracting and predicting every 5 tags
    index = 1
    tag_list = soup.find_all('p', attrs={'data-p-id': True})
    for p_tag in tag_list:
        if show_progress and index % 5 == 0:
            print('Extracting tag no.' + str(index) + 'out of '+ str(len(tag_list)) + '...')
        # Check if the <p> tag contains any <span> tags
        if p_tag.find('span'):
            # Remove text from nested <span> tags
            for span_tag in p_tag.find_all('span'):
                span_tag.extract()
        # Extract the text from the <p> tag and evaluate it
        p_text = p_tag.get_text(strip=True).rstrip('\n')           
        if show_progress and index % 5 == 0:
            print('Predicting tag no.' + str(index) + 'out of '+ str(len(tag_list)) + '...')     
        # Get list of <p> data-p-id
        if True:
            response.append([p_tag.get('data-p-id'), 'tmp']) # to bo implemented Thái
        if show_progress and index % 5 == 0:
            print('Finish tag no.' + str(index) + 'out of '+ str(len(tag_list)) + '...')
        index += 1
    return json.dumps(response)

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
