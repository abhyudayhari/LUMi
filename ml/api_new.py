from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, AutoModelForSeq2SeqLM,AutoModelForTextEncoding,Wav2Vec2ForCTC,AutoProcessor
import transformers
import torch
import torchaudio
from huggingface_hub import login
from transformers import TextStreamer
import re
from dotenv import load_dotenv
load_dotenv() 
from tools import *
from datetime import date
import random
from fastapi import FastAPI, HTTPException, Request,Response
import os
import re
import glob
import json
import tempfile
import math
import requests
from starlette.datastructures import Headers

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather  
        
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.getenv('TWILIO_NUMBER')
URL=os.getenv("URL")
TO_NUM = os.getenv("TO_NUM")
print(TWILIO_ACCOUNT_SID,TWILIO_ACCOUNT_SID,TWILIO_NUMBER,TO_NUM)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
# print("env values:", TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER, URL, TO_NUM, GKEY)

uuid = ''
l = []
k = 1
lang = "en-IN"
dic = {'1': 'en-IN', '2': 'hi-IN', '3': 'kn-IN', '4': 'zh-CN'}#,"5":'ta-IN'}  # 0 style for kan and beng
call = s = None
    

app=FastAPI()
# Get only today's date
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import time
## loading the models##########

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"#"meta-llama/Llama-3.2-3B"#"microsoft/phi-2"#"meta-llama/Meta-Llama-3.1-8B-Instruct"

# login(hf_token)

bnb_config = transformers.BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)
model=AutoModelForCausalLM.from_pretrained(model_id,quantization_config=bnb_config, trust_remote_code=True,device_map='auto')
tokenizer = AutoTokenizer.from_pretrained(model_id)
model.config.pad_token_id = model.config.eos_token_id


###############Translational Model #############
translational_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
translational_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M",quantization_config=bnb_config).to("cuda")
###############ASR MODEL############
asr_model_id = "facebook/mms-1b-l1107"
asr_processor = AutoProcessor.from_pretrained(asr_model_id)#.to('cuda')
asr_model = Wav2Vec2ForCTC.from_pretrained(asr_model_id).to('cuda')

#streamers

streamer = TextStreamer(tokenizer, skip_prompt=True)
translation_streamer=TextStreamer(translational_tokenizer, skip_prompt=True)

########defining tools


part_1_tools=[
    fetch_user_personal_details,
    #TavilySearchResults(max_results=5),
    online_search,
    # update_user_info,
    room_booking_info,
    add_grievances,
    fetch_food_items,
    fetch_food_order,
    delete_food_order,
    delete_grievances,
    change_food_order,
    retrieve_all_user_bookings,
    fetch_complaints,
    give_food_order,
    change_grievances,
    delete_room_service_tasks,
    change_room_service_tasks,
    add_room_service_tasks,
    fetch_room_service_tasks
    
]

###function calling function#########

def function_call(input_string:str):

    if input_string[0]!="{":
        pattern = r'<function>(.*?)</?function>' 
        
        matches_str = re.findall(pattern, input_string)
        if len(matches_str)>0:
            matches_str=matches_str[0]
        else:
            return {"name":"Error","fn_output":"Error in function call, Recheck the name and the parameters"}
        matches=eval(matches_str)
    # print(matches)
    else:
        matches_str=input_string
        matches=eval(input_string)
    # print(matches," str:",matches_str)
    func_name=matches["name"]
    
    arguments=matches["parameters"]
    # print(type(arguments))
    try:
        #print({"Arguments":arguments,"Func_name":func_name})
        if len(arguments)>0:
            # print(arguments)
            if not isinstance(arguments,dict):
                arguments=eval(arguments)
            output=globals()[func_name](**arguments)
        else:
            output=globals()[func_name]()
        form=input_string.replace(matches_str,"").replace("<function>","").replace("</function>","")
        if len(form)==0:
            form=None
        return {"name":func_name,"formatted_output":form,"fn_output":output}
    except:
        return {"name":func_name,"fn_output":"Error in function call, Recheck the name and the parameters"}
    # except:
    #     output=globals()[func_name]()


class bookings():
    def __init__(self):
        self.booking_chats={}

    def get_or_create_booking_chats(self,booking_id,content=None):
        if booking_id not in self.booking_chats:
            booking_details=room_booking_info(booking_id)
            user_id,room_no=booking_details["User_id"],booking_details["Room No"]
            current_date=date.today()
            self.booking_chats[booking_id]=[{"role":"system","content": f"""You are LUMI, a helpful personal assistant for customers of  Lyf Funan Hotel, Singapore. Also help them with their general questions about the Hotels etc. \n
                 Use the provided tools to  fetch user details, take complaints, take food orders , and other information to assist the user's queries. \n 
                 When searching, be persistent. Expand your query bounds if the first search returns no results. \n
                 If a search comes up empty, expand your search before giving up. If you dont find an appropriate tool just say " I dont know, would you like to contact a hotel personenl?" If the final result is empty then, just try to answer the question with your own language.
                 \n
                \n\n<User>Current user:{user_id}\n
            Room No: {room_no},
            Booking_id: {booking_id} ,
           
            </User>
                \nCurrent date: {current_date}.
                
           
                """},         
            {"role":"system","content":"You a helpful hotel  assistant, when given an output from a tool, wrap it around with a natural language text so that its easy to understand and give a confirmation to the user that it is done. If the output tell the user to see the respective documents.\n"},
            {"role":"system","content":"When you are given questions which are not related to any above given tool, just answer it with your knowledge and stick to hotel information .Keep it short.\n"},
          {"role":"system","content":"DO NOT ASSUME THINGS BY YOURSELF ASK THE USER FIRST\n"},
          {"role":"system","content":"You are answering to the actual so dont tell him what functions are being called.\n"},
          {"role":"system","content":"KEEP THE ANSWERS SHORT!!!!\n"},
          
         {"role":"system","content":"""If you choose to call a function wrap it around <function> tags\n For example:\n <function>{"name":"function_name","parameters":{"parameter_name":parameter_value}}<function>, if you dont add the special tags, then it will lead to nuclear war!!!"""},
         {"role":"system","content":"Add the special <function> tags before and after the function call or you will be killed immediately"},
          {"role":"system","content":"If the tool is showing error then say, sorry for the inconvinience, right now I am facing some technical difficulties"},
        {"role":"system","content":"KEEP THE ANSWERS VERY VERY VERY **SHORT**!!!! ANSWER IN ***ONE LINE ONLY*** and within ****10 WORDS ONLY****!!!!!!!!\n"}
         ]
        if content!=None:
            self.booking_chats[booking_id].append(content)
        return self.booking_chats[booking_id]

# class chats_retrieval()
#     def __init__(self):
#         self.booking_chats=bookings()
#     def chat(booking_id,content):
#         return 
waiting_messages=["Please hold on for a moment while we complete the operation.!!!","Thank you for your patience; your request is being handled.","Just a moment, we're processing that for you.","Please bear with us; your operation is underway."]

booking_chats=bookings()
#voice_response = VoiceResponse()
@app.post("/api/say/")
async def formatted_output_say(request:Request):
    print("hello")
    body = await request.json()
    text = body.get("text")
    lang = body.get("lang")
    timeout = body.get("timeout",120)
    # text,lang,timeout=120
    response = VoiceResponse()
    response.say(text)#,language=lang,timeout=timeout)
    print(str(response))
    return Response(content=str(response), media_type="application/xml")

from fastapi.responses import JSONResponse


@app.post("/api/whatsapp_api/")
async def whatsapp_multi_lang_api(request: Request):
    # print("hello hi kaise ho")
    body = await request.json()
    booking_id = body.get("booking_id")
    user_input = body.get("user_input")
    language = body.get("language")
    streaming = body.get("streaming", False)  # Default to False if not provided

    # print("Hello laude!!!!")
    eng_flag=False
    language_codes={"Hindi":{"translation_lang_code":"hin_Deva"},"Kannada":{"translation_lang_code":"kan_Knda"},"Chineese":{"translation_lang_code":"zho_Hans"}}
    response=""
    if language=="English":
        eng_flag=True
    else:
        translation_lang_code=language_codes[language]["translation_lang_code"]
    if not eng_flag:
        translational_inputs= translational_tokenizer(user_input, return_tensors="pt",).to("cuda")
        translated_tokens = translational_model.generate(
        **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids("eng_Latn"),max_length=1024)#256)#1024)
        translated_text=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"user","content":translated_text})
    else:
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"user","content":user_input})

    inputs=tokenizer.apply_chat_template(user_chats, tools=part_1_tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    # if eng_flag:
    out = model.generate(**inputs, max_new_tokens=96)#64)#128)#192)#256)#1024) #,
    output=tokenizer.decode(out[0][len(inputs["input_ids"][0]):],skip_special_tokens=True)
    print("THe output is      \n",output)
    user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":output})
    if ("<function>"  in output) or ("{" in output):
        # tool_start_time=time.time()
        fn_output=function_call(output)
        print(fn_output)
        tool_output,func_name=fn_output["fn_output"],fn_output["name"]
        
        if "formatted_output"  in fn_output.keys(): 
            formatted_str=fn_output["formatted_output"]
            if formatted_str==None:
                formatted_str=waiting_messages[random.randint(0,len(waiting_messages)-1)]
            if not eng_flag:
                translational_inputs = translational_tokenizer(formatted_str, return_tensors="pt",).to("cuda")
                if streaming:
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
                else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
                    
                    translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
                    response+=translational_output+"\n"
                    #print(translational_output)
            else:
                response+=formatted_str+"\n"#print(formatted_str)
        else:
            pass 
    
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":f"The output from the tool {func_name} is  {tool_output}"})
        inputs=tokenizer.apply_chat_template(user_chats, tools=part_1_tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        # if eng_flag:
        if eng_flag and streaming:
            out = model.generate(**inputs, streamer=streamer,max_new_tokens=96)#1024) #,
        else:
            out=model.generate(**inputs,max_new_tokens=96)#64)#128)#192)#256)#1024) 
        output=tokenizer.decode(out[0][len(inputs["input_ids"][0]):],skip_special_tokens=True)
        # print("THe output from model is      \n",output)
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":output})
        if not eng_flag:
            translational_inputs = translational_tokenizer(output, return_tensors="pt",).to("cuda")
            if streaming:
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
            else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
                    
            translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            #print(translational_output)
            response+=translational_output+"\n"
        else:
            #print(output)
            response+=output+"\n"
    
    else:
        if  eng_flag:
            # print(output)
            response+=output+"\n"
        else:
            translational_inputs = translational_tokenizer(output, return_tensors="pt",).to("cuda")
            if streaming:
                    
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
            else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
            # print("hello")
            translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            #print(translational_output)   
            response+=translational_output+"\n"
    return {"message":response}
    
    
@app.api_route("/api/call_api/")
async def call_multi_lang_api(request: Request):
    # print("hello hi kaise ho")

    body = await request.json()
    booking_id = body.get("booking_id")
    user_input = body.get("user_input")
    language = body.get("language")
    streaming = body.get("streaming", False)  # Default to False if not provided
    call=body.get("call",False)


    eng_flag=False
    language_codes={"Hindi":{"translation_lang_code":"hin_Deva"},"Kannada":{"translation_lang_code":"kan_Knda"},"Chineese":{"translation_lang_code":"zho_Hans"}}
    response=""
    if language=="English":
        eng_flag=True
    else:
        translation_lang_code=language_codes[language]["translation_lang_code"]
    if not eng_flag:
        translational_inputs= translational_tokenizer(user_input, return_tensors="pt",).to("cuda")
        translated_tokens = translational_model.generate(
        **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids("eng_Latn"),max_length=1024)
        translated_text=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"user","content":translated_text})
    else:
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"user","content":user_input})

    inputs=tokenizer.apply_chat_template(user_chats, tools=part_1_tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    # if eng_flag:
    out = model.generate(**inputs, max_new_tokens=1024) #,
    output=tokenizer.decode(out[0][len(inputs["input_ids"][0]):],skip_special_tokens=True)
    # print("THe output is      \n",output)
    
    user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":output})
    if ("<function>"  in output) or ("{" in output):
        # tool_start_time=time.time()
        fn_output=function_call(output)
        tool_output,func_name=fn_output["fn_output"],fn_output["name"]
        if "formatted_output"  in fn_output.keys(): 
            formatted_str=fn_output["formatted_output"]
            if formatted_str==None:
                formatted_str=waiting_messages[random.randint(0,len(waiting_messages)-1)]
            if not eng_flag:
                translational_inputs = translational_tokenizer(formatted_str, return_tensors="pt",).to("cuda")
                if streaming:
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
                else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
                    
                    translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
                    
                    
                    if call==True:
                        response=VoiceResponse()
                        response.say(translational_output,language=lang)                      

    
    # Call the endpoint function directly
                        response = await formatted_output_say(request)
                
                        print(response)
                        # formatted_output_say(translational_output,lang)
                        

                    else:
                        response+=translational_output+"\n"
                        
                
            else:
                if call==True:
                      response=VoiceResponse()
                      response.say(formatted_str)

                else:
                    response+=formatted_str+"\n"#print(formatted_str)
                
        else:
            pass 
    
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":f"The output from the tool {func_name} is  {tool_output}"})
        inputs=tokenizer.apply_chat_template(user_chats, tools=part_1_tools, add_generation_prompt=True, return_dict=True, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        # if eng_flag:
        if eng_flag and streaming:
            out = model.generate(**inputs, streamer=streamer,max_new_tokens=1024) #,
        else:
            out=model.generate(**inputs,max_new_tokens=1024) 
        output=tokenizer.decode(out[0][len(inputs["input_ids"][0]):],skip_special_tokens=True)
        # print("THe output from model is      \n",output)
        user_chats=booking_chats.get_or_create_booking_chats(booking_id,content={"role":"assistant","content":output})
        if not eng_flag:
            translational_inputs = translational_tokenizer(output, return_tensors="pt",).to("cuda")
            if streaming:
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
            else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
                    
            translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            #print(translational_output)
            response+=translational_output+"\n"
        else:
            #print(output)
            response+=output+"\n"
    
    else:
        if  eng_flag:
            # print(output)
            response+=output+"\n"
        else:
            translational_inputs = translational_tokenizer(output, return_tensors="pt",).to("cuda")
            if streaming:
                    
                    translated_tokens = translational_model.generate(
          **translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),streamer=translation_streamer, max_length=1024
          )
            else:
                    translated_tokens = translational_model.generate(**translational_inputs, forced_bos_token_id=translational_tokenizer.convert_tokens_to_ids(translation_lang_code),max_length=1024
          )
            # print("hello")
            translational_output=translational_tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
  
            response+=translational_output+"\n"

    return {"message":response}
    #return Response(content=str(response), media_type="application/xml")





    
   


@app.api_route("/", methods=['POST','GET'])

def call():
    global uuid,call
    l.clear()
    call = s = None
    k = 1
    uuid = ''
    print("lauda")
    call = client.calls.create(
        to=TO_NUM,
        from_=TWILIO_NUMBER,
        # machine_detection='Enable',
        # machine_detection_timeout=10,
        url=f'{URL}/twiml',
        method='POST',
        
    )
    uuid = call.sid
    call = client.calls(uuid)
    print("Before payload")
    # Make a POST request to the specified URL
    payload = {
        'isCallOngoing': True,
        'isCallEnded': False,
        'isChatMessage': False
    }
    

@app.api_route('/twiml', methods=['POST'])
def twiml():
    global k, lang
    print("Error occurred after /twiml")
    response = VoiceResponse()
    print("Error occurred in gathering")
    print(f'{URL}/webhooks/input')
    gather = Gather(num_digits=1, action=f'{URL}/webhooks/input')
    print("here")
    gather.say('This call is being recorded for training purposes')
    gather.say('Press 1 for English')
    gather.say('हिन्दी के लिए 2 दबाएँ',language='hi-IN')
    #gather.say('ಕನ್ನಡಕ್ಕಾಗಿ 3 ಒತ್ತಿರಿ',language='kn-IN')
    gather.say('中文请按 3',language='zh-CN')
    
    response.append(gather)
   
    return Response(content=str(response), media_type="application/xml")

@app.api_route('/webhooks/input', methods=['POST'])
async def handle_input(request: Request):#request:Request):
    body = await request.form()  # Use `await request.form()` to parse form data
    digits = body.get('Digits', None) 
    print("DIGITS:",digits)
    # print("Error occurred after handle input")
    global k, lang, s
    
    if digits :
        l.append({1: 'Hello! When I stop speaking, please ask your query and wait for 3 seconds.', 2: 'नमस्कार। जब मैं बोलना बंद कर दूं, तो कृपया अपना प्रश्न पूछें और 3 सेकंड प्रतीक्षा करें।' ,  3: "你好！当我停止讲话时，请提出您的疑问并等待 3 秒钟。"}.get(int(digits), 'Hello! When I stop speaking, please ask your question and wait for 3 seconds.'))
        lang = dic.get(digits, 'en-IN')
    response = VoiceResponse()
    if digits == '0':
        response.say('Goodbye',timeout=120)
    else:
        print(f"DONE {k}")
        response.say(l[-1], language=lang,timeout=120)
        gather = Gather(input="speech", language=lang, action=f'{URL}/webhooks/recordings', speech_timeout=3)
        # gather.say(l[-1], language=lang)
        response.append(gather)
        s = datetime.now()
    k += 1
    print(response.__str__(), response.__dir__())
    # return str(response)
    return Response(content=str(response), media_type="application/xml")

dummy_resp=1
@app.api_route('/webhooks/recordings', methods=['POST'])
async def handle_recordings(request: Request):
    global dummy_resp
    # print("Error occurred after this")
    # print(request, request.values)
    body = await request.form()
    transcription = body.get('SpeechResult', None)
    # transcription = request.values.get('SpeechResult')
    print(" Transcription",transcription)
        
    booking_id="03c8788c-b569-49b1-aa91-396d87433057"
    language_codes1={"en-IN":"English","hi-IN":"Hindi","kn-IN":"Kannada","zh-CN":"Chineese"}
    for _ in range(3):
        try:
            
            payload={"booking_id":booking_id,"user_input":transcription,"language":language_codes1[lang],"call":True}
            headers = Headers({"content-type": "application/json"})
            request = Request(scope={"type": "http", "method": "POST", "path": "/api/call_api/", "headers": headers}, receive=None)

    # Manually set the JSON body for the request
            request._body = json.dumps(payload).encode("utf-8")
    
   # # Call the endpoint function directly
            response = await call_multi_lang_api(request)
            response_model=response.get("content")
            response_model=response["message"]

            l.append(response_model)
            dummy_resp+=1
            break
        except Exception as e:
            print(f"Error in model generation: {e}")
            pass

    response = VoiceResponse()

    response.redirect(f'{URL}/webhooks/input')
    print(datetime.now() - s)

    return Response(content=str(response), media_type="application/xml")
    # return str(response)
