import transformers
pipe = transformers.pipeline(model="typeform/distilbert-base-uncased-mnli", task="zero-shot-classification")

def contain_a_z(text: str):
    # function: check if input text have any char from a to z    
    for char in text:        
        int_rep = ord(char.lower())
        if int_rep in range(97, 123):
            return True
    return False

# define a function to standardize text
def standardize_text(text:str):
    # only keep characters from a-z and A-Z and space
    for char in text:
        if not char.isalpha():
            text = text.replace(char, '')        
    return text
    

# define a function to parse paragraph into sentences
def parse_paragraph(paragraph:str):          
    sentences = paragraph.split('.')    
    # remove sentences without any alphabetic characters
    for sentence in sentences:
        if not any(ch.isalpha() for ch in sentence):
            sentences.remove(sentence)
            continue
        for ch in ['  ', '   ', '    ', '     ', '      ']:
            sentence = sentence.replace(ch, ' ')
        # remove spaces at the beginning of sentences or end of sentences
        if sentence[0] == ' ':
            sentence = sentence[1:]
        if sentence[-1] == ' ':
            sentence = sentence[:-1]  
    return sentences



def change_text(input: str):
    # function: change input text to placeholder
    # para: input: input text
    # return: output: placeholder text (same length with input text, only contain 'X')
    output = ''
    for char in input:
        output += 'X'
    return output

def match_label(text: str, target_label: str, threshold = 0.8):
    global pipe        
    if not contain_a_z(text):
        return False
    output = pipe(text, target_label, multi_label=False)            
    if output['scores'][0] >= threshold:        
        return True
    return False

def init_queue(text_list:list, bucket_len = 512):    
    # para: text_list: list of text in each tag
    #      bucket_len: maximum length of concatenated text, larger num = faster runtime  (default = 512)
    # return queue: queue of index range that have not been checked        
    queue = [] 
    n = len(text_list)
    index = 0
    while index < n:
        current_text_len = 0
        low = index
        # accumulate text until length >= 512
        while index < n:
            current_text_len += len(text_list[index])
            if index != n-1 and current_text_len + len(text_list[index+1]) < bucket_len:
                index += 1        
            else:
                break
        high = index                        
        queue.append((low, high))
        index += 1
    return queue

def clear_non_label(range_list: list, text_list:list, label: str):
    # function: delete bucket that does not match with label         
    # para: range_list: list of range to check        
    # return cleared_list: queue of index range that match with label                
    for item in range_list:
        # recreate text in range
        current_text = ''
        for index in range(item[0], item[1] + 1):
            current_text += text_list[index]
        # check if current_text match with label
        if not match_label(current_text, label):
            # delete range from queue
            range_list.remove(item) 
    return range_list    

def find_label_index(range_queue: list, text_list:list, label: str):
    # function: find index of tag match with label using binary search
    # para: range_queue: list of range to check
    #       text_list: list of text in each tag
    # return matched_text: list of range match label (precision down to one tag)
    matched_text = []
    while len(range_queue) > 0:
        low, high = range_queue.pop(0)    
        if low > high:
            continue
        elif low == high: # range only contain a single tag
            matched_text.append((low, high))
        else:        
            mid = (low + high) // 2
            # handle each half                
            # recreate text in range
            current_text = ''
            for index in range(low, mid + 1):
                current_text += text_list[index]
            # check further if range match with label
            if match_label(current_text, label):
                range_queue.append((low, mid))
            # do like so with the second half            
            current_text = ''
            for index in range(mid + 1, high + 1):
                current_text += text_list[index]
            if match_label(current_text, label):
                range_queue.append((mid +1, high))
    return matched_text

def find_content_id(tag_text: list, id:list, label: str):    
    res_text = [] # list of text that match with label (maybe edited)
    res_id = [] # list of id that correspond to res_text 
# standardize input text
    # for index in range(len(tag_text)):
    #     tag_text[index] = standardize_text(tag_text[index])
# find label on tag level
    # initialize queue of index range to be checked      
    queue = init_queue(tag_text, 200)
    # clear range that does not match with label
    queue = clear_non_label(range_list= queue, text_list= tag_text, label= label)
    # find index of tag match with label using binary search
    tag_index = find_label_index(range_queue= queue, text_list= tag_text, label= label)            
# find label on sentence level
    index_dict = {} # index of tag_text and tag_id in input that contain each sentence
    # break down each tag into sentences and bind the sentences to tag's id
    sentence_text = []
    for tag in tag_index:
        index , high = tag        
        # parse paragraph into sentences    
        sentences = parse_paragraph(tag_text[index])        
        # create a dictionary of sentence to id
        for sentence in sentences:
            index_dict[sentence] = index
            sentence_text.append(sentence)
# find label in sentence level by doing the same thing with paragraph level
    queue = init_queue(text_list=sentence_text, bucket_len=50)
    queue = clear_non_label(range_list= queue, text_list= sentence_text, label= label)
    sentence_index = find_label_index(range_queue= queue, text_list= sentence_text, label= label)
    # create new sentence from ones matched with label
    for sentence in sentence_index:
        index, high = sentence
        # get index of tag that contain current sentence
        base_index = index_dict[sentence_text[index]]
        # get id of tag that contain current sentence
        old_id = id[base_index]                     
        # replace the sentence in tag with placeholder
        old_text = tag_text[base_index]        
        new_text = old_text.replace(tag_text[base_index], change_text(sentence_text[index]))        
        # add new_text and id to result
        res_id.append(old_id)
        res_text.append(new_text)
    return res_text, res_id