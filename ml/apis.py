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
# Get only today's date


#### loading the models##########

model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

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
          {"role":"system","content":"Keep the answers short!!!!\n"},
          
         {"role":"system","content":"""If you choose to call a function wrap it around <function> tags\n For example:\n <function>{"name":"function_name","parameters":{"parameter_name":parameter_value}}<function>, if you dont add the special tags, then it will lead to nuclear war!!!"""},
         {"role":"system","content":"Add the special <function> tags before and after the function call or you will be killed immediately"},
          {"role":"system","content":"If the tool is showing error then say, sorry for the inconvinience, right now I am facing some technical difficulties"},
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
def whatsapp_multi_lang_api(booking_id,user_input,language,streaming=False):
    eng_flag=False
    language_codes={"Hindi":{"translation_lang_code":"hin_Deva"},"Kannada":{"translation_lang_code":"kan_Knda"}}
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
        # tool_end_time=time.time()
        # print("Time taken by tool:",tool_end_time-tool_start_time)
        # messages.append({"role":"assistant","content":output})
        tool_output,func_name=fn_output["fn_output"],fn_output["name"]
        # print(fn_output)
        # print("The formatted string is : \n",formatted_str,"\n")
        # print("The tool output is : \n",tool_output)
        # print(fn_output)
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
                    print(translational_output)
            else:
                print(formatted_str)
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
            print(translational_output)
        else:
            print(output)
    
    else:
        if  eng_flag:
            print(output)
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
            print(translational_output)   
        
    
        
        
    
    
    
    
    
    


    
   