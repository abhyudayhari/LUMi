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

# Get only today's date


#### loading the models##########

main_streamer = TextStreamer(tokenizer, skip_prompt=True)
translation_streamer=TextStreamer(translational_tokenizer, skip_prompt=True)
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

login(hf_token)

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

##########defining tools

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
    def __init___(self):
        self.booking_chats={}

    def get_or_create_booking_chats(self,booking_id,content):
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
          {"role":"system","content":"Keep the answers short!!!!\n"},
          
         {"role":"system","content":"""If you choose to call a function wrap it around <function> tags\n For example:\n <function>{"name":"function_name","parameters":{"parameter_name":parameter_value}}<function>, if you dont add the special tags, then it will lead to nuclear war!!!"""},
         {"role":"system","content":"Add the special <function> tags before and after the function call or you will be killed immediately"},
          {"role":"system","content":"If the tool is showing error then say, sorry for the inconvinience, right now I am facing some technical difficulties"},
         ]
        self.booking_chats[booking_id].append(content)
        return self.booking_chats[booking_id]
    # def modify_chats(self,booking_id,content):
    #     self.booking_chats[booking_id].append(content)
    #     return self.booking_chats

# class chats_retrieval()
#     def __init__(self):
#         self.booking_chats=bookings()
#     def chat(booking_id,content):
#         return 

def whatsapp_multi_lang_api(booking_id,content,language):
    language_codes={"Hindi":{"translation_lang_code":


    
   