import firebase_admin
from firebase_admin import credentials,db

cred = credentials.Certificate("hackglobal-df446-firebase-adminsdk-9mubj-740934f8e4.json")
firebase_admin.initialize_app(cred)
from firebase_admin import firestore
import json
import uuid
from datetime import datetime
import random
# from dotenv import load_dotenv
# load_dotenv() 
from langchain_community.tools.tavily_search import TavilySearchResults
# Get the current date and time

db=firestore.client()
users=db.collection("Users")
room_reservations=db.collection("Room_bookings")
grievances=db.collection("Grievances")
hotel_personnel=db.collection("Hotel_repair_personnel")
food_items=db.collection("Food_Items")
food_orders=db.collection("Food_Orders")
room_service_task=db.collection("Room_service_task")

def give_timestamp():
    now = datetime.now()

# Format the current date and time
    formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
    return str(formatted_now)

def give_id():
    return str(uuid.uuid4())
def online_search(input_query:str)->list[dict]:
    """ Searches online for relevent result.
        Args:
            input_query: (str) A detailed and informative query which can be searched online.

            
        Returns:
            A list of dictionary having the urls and description of the top search results.
    """
   
    query=TavilySearchResults(max_results=5)
    return query(input_query)
    
def fetch_user_personal_details(user_id:int)-> dict:
    """ Fetches user data from database.
        Args:
            user_id: (int) The user id of the user.

        Returns:
            The personal details of the user including information of user's Background , Identification_doc_type, Document_id, Age, VIP, Name, Married, User_id as a dictionary
    """
    if not user_id:
            return "No user id configured"
    query=users.where("User_id",'==',user_id)
    results=query.stream()
    output=[]
    for details in results:
        output.append(details.to_dict())
    if len(output)==0:
         return "Incorrect user id "
    return output[0]



def retrieve_booking_ref(user_id:int)->list:
     """Fetches all the Booking ids of a specific user from the database.
        Args:
            user_id: (int) The user id of the user.
     """  
     if not user_id:
         return "No user id configured"
     booking_query=room_reservations.where("User_id","==",user_id)
     results=booking_query.stream()
     output=[]
     for details in results:
        output.append(details.to_dict()["Booking_id"])
     if len(output)==0:
        return "No bookings with the specified user id."
     return output



def update_user_info(user_id:int,update_fields:dict)->bool:
      """Updates the information about the user present in the database.
         Args:
            user_id: (int) The user id of the user.
            update_fields: (dict) A dictionary of the changes, where key is the changed attribute name and the value is updated value. (choices for attribute name : ["Age", "Background", "Name"])
         Returns:
             True or False based on the success of the operation."""
      user_query=users.where("User_id",'==',user_id).stream()
      try:
         for user in user_query:
            user_ref = users.document(user.id)
            user_ref.update(update_fields)
         return True
      except:
          return False
      
def room_booking_info(booking_id:str)->dict:
    """ Fetches the booking details from the database provided a booking id.
        Args:
            booking_id: (str) The booking id of the user.
            
        Returns: 
            It returns the booking details including the Checkin time, Checkout time, Duration period, Price paid, Room no, Room incharge's name, User id """
    if not booking_id:
        return "No Booking reference given."
    booking_query=room_reservations.where("Booking_id","==",booking_id)
    results=booking_query.stream()
    output=[]
    for details in results:
        output.append(details.to_dict())
    if len(output)==0:
        return "Incorrect booking reference value."
    return output[0]

def retrieve_all_user_bookings(user_id:int)->list[dict]:
    """Retrieves all the booking id of a specific user
       Args:
            user_id: (int) The user id of the user. 
       Returns:
           A list of dictionary containing details of all the previous and current booking with the hotel."""
    booking_ids=retrieve_booking_ref(user_id)
    bookings=list()
    for booking_id in booking_ids:
        bookings.append(room_booking_info(booking_id))
    return bookings

def get_hotel_personnel_type(type:str)->dict:
    """ Retrieves hotel personnel details """
    if not type:
        return "No type of complaint provided"
    personnel_query=hotel_personnel.where("Type_of_service","==",type)
    results=personnel_query.stream()
    output=[]
    for personnel in results:
        output.append(personnel.to_dict())
    if len(output)>1:
        return output[random.randint(0,len(output)-1)]
    else:
        return output
    
def add_grievances(booking_id:str,description:str,type:str)->str:
    """ Adds user grievances to the grievances to the database.
        Args:
            booking_id: (str) The booking id of the user.
            description: (str) The exact description of the greivance or complaint.
            type: (str) The department concerned. (choices: ["Plumbing", "Electrical", "Network", "Housekeeping"])
            
        Returns:
            A complaint_id which the user can refer, or an error message"""
    
    if not booking_id or not description or not type:
          return "Atleast one input not provided"
    booking_info=room_booking_info(booking_id)
    room_no,user_id=booking_info["Room No"],booking_info["User_id"]
    try:
        inp={"Complaint_id":give_id(),"Description":description,
            "Resolved":False,"Room No":room_no,
            "Time Lodged":give_timestamp(),
            "Type":type,
            "User_id":user_id,
            "Booking_id":booking_id}
        complaint_id=inp["Complaint_id"]
        personnel=get_hotel_personnel_type(inp["Type"])
        doc_ref=grievances.document(str(complaint_id))
        inp["Assigned_person_id"]=personnel["Emp_id"]
        doc_ref.set(inp)
        return complaint_id
    except:
        
  
       return "Not able to register a complaint!"


def change_grievances(complaint_id:str,changed_description:str)->bool:
    """ Change the grievance made by the user in the database on the basis of given complaint id.
        Args:
            complaint_id: (str) The complaint id of the grievance or the complaint.
            changed_description: (str)  A apt description the issue faced.
        Returns:
            True or False based on the success of the operation."""
    if not changed_description or not complaint_id:
        return "Atlease one field missing!"
    grievances_query=grievances.where("Complaint_id",'==',complaint_id).stream()
    try:
        count=0
        for complaint in grievances_query:
            grievances_ref = grievances.document(complaint.id)
            grievances_ref.update({"Description":changed_description})
            count+=1
        if count>0:
            return True
        else:
            return False
    
    except:
        
        return False

# def fetch_grievances_complaint(complaint_id:str)->dict:
#     """ Fetches Grievances from the database on the basis of complaint id."""
#     if not complaint_id :
#             raise ValueError("Complaint id not provided is missing")
#     query=grievances.where("Complaint_id",'==',complaint_id)
#     results=query.stream()
#     output=[]

#     for details in results:
#         output.append(details.to_dict())
    
#     return output[0]

def fetch_complaints(booking_id:str)->list[dict]:
    """Fetches the Grievances lodged by user from the database.
       Args:
            booking_id: (str) The booking id of the user.
       Returns:
            A list of dictionary containing details about each complaint regarding a give booking id
    """
    if not booking_id :
           return "Complaint id not provided is missing"
    query=grievances.where("Booking_id",'==',booking_id)
    results=query.stream()
    output=[]

    for details in results:
        output.append(details.to_dict())
    if len(output)==0:
        return "No complaints popped up!"
    return output


def fetch_food_items()->list[dict]:
    """ Fetches all the food items present in the database.
        Returns:
                A list of dictionary where each dictionary has the data about a particular food item."""
    food_items_db=food_items.stream()
    food_item=[]
    for item in food_items_db:
        food_item.append(item.to_dict())
    return food_item


def give_food_order(booking_id:str,items:list[str],price:int)->str:
    """ Orders food on the behalf of the user and adds them to the database.
        Args:
            booking_id: (str) The booking id of the user.
            items: (list) A list containing Item_id of food items ordered by the user.
            price: (int) The total price of the orders.
        Returns:
            A string containing the order id if the order was successfull or an error message if the order failed."""
    
    if not booking_id or not items or not price:
        return "Atleast one value is missing"
        
    order={"Order_id":give_id(),"Order":items,"Ordered_time":give_timestamp(),"Price":price,
           "Booking_id":booking_id,
           "Delivered":False}
    
    doc_ref=food_orders.document(str(order["Order_id"]))
    doc_ref.set(order)
    return order["Order_id"]
   


def change_food_order(Order_id:str,changes:dict)->bool:
    """ Changes the food order already present in the database.
        Args:
            Order_id: (str) The order id of the food order.
            changes: (dict) A dictionary with changes, where keys are attribute name and the values are changed values (choices for attribute name : ["Order", "Price"]). If the attribute name is "Order" then the value contains a list of Item_id of the food items.    
        Returns:
            True or False based on the success of the change."""
    if not Order_id or not changes:
        return "Atleast one value is missing!"
    order_query=food_orders.where("Order_id",'==',Order_id).stream()
    try:
        count=0
        for order in order_query:
            order_ref = food_orders.document(order.id)
            order_ref.update(changes)
            count+=1
        if count>0:
            return True
        else:
   
            return False
        
    except:
        
        return False
    
def add_room_service_tasks(booking_id:str,description:str)->str:
    """ Adds user given task to be completed by room service in the database.
        Args:
            booking_id: (str) The booking id of the customer.
            description: (str) The task given by the user to be completed by the room service personnel.
        Returns:
            A room_service_task_id which the user can refer, or an error message.
    """
    if not booking_id or not description :
          return "Atleast one input not provided"
    booking_info=room_booking_info(booking_id)
    room_no,user_id=booking_info["Room No"],booking_info["User_id"]
    try:
        inp={"room_service_task_id":give_id(),"Description":description,
            "Done":False,"Room No":room_no,
            "Time Lodged":give_timestamp(),
            "User_id":user_id,
            "Booking_id":booking_id}
        room_service_task_id=inp["room_service_task_id"]
        # personnel=get_hotel_personnel_type(inp["Type"])
        doc_ref=room_service_task.document(str(room_service_task_id))
        # inp["Assigned_person_id"]=personnel["Emp_id"]
        doc_ref.set(inp)
        return room_service_task_id
    except:    
       return "Not able to register a room service task!"

def change_room_service_tasks(room_service_task_id:str,changed_description:str)->bool:
    """ Changes the room srevice task made by the user in the database on the basis of given room service task id.
    
        Args:
            room_service_task_id: (str) The room service task  id of the grievance or the task.
            changed_description: (str)  A apt description of the task be done.
        Returns:
            True or False based on the success of the operation."""
    if not changed_description or not room_service_task_id:
        return "Atlease one field missing!"
    task_query=room_service_task.where("room_service_task_id",'==',room_service_task_id).stream()
    try:
        count=0
        for task in task_query:
            grievances_ref = room_service_task.document(task.id)
            grievances_ref.update({"Description":changed_description})
            count+=1
        if count>0:
            return True
        else:
            return False
    
    except:
        
        return False

def delete_room_service_tasks(room_service_task_id:str)->bool:
    """ Deletes  Room service task  on the basis of room_service_task_id.
        Args:
            room_service_task_id: (str) The room_service_task_id of the task  to be deleted.
        Returns:
            True or False based on the success of the deletion."""
    if not room_service_task_id:
        return "Missing room_service_task_id"
    try:
        query=room_service_task.where("room_service_task_id",'==',room_service_task_id)
        results=query.stream()
        for details in results:
            details.reference.delete()
        return True
    except:
        return False

def fetch_room_service_tasks(booking_id:str)->list[dict]:
    """Fetches the Room Service tasks given  by user from the database.
       Args:
            booking_id: (str) The booking id of the user.
       Returns:
            A list of dictionary containing details about each room service task regarding a give booking id
    """
    if not booking_id :
           return "Booking id not provided is missing"
    query=room_service_task.where("Booking_id",'==',booking_id)
    results=query.stream()
    output=[]

    for details in results:
        output.append(details.to_dict())
    if len(output)==0:
        return "No room service task popped up!"
    return output

def fetch_food_order(Booking_id:str)->list[dict]:
    """ Fetches the food order from the database on the basis of Booking_id of the customer.
        Args:
            Booking_id: (str) The booking_id of the user.
        Returns:
            A list of dictionary where each dictionary contains the details of unique order from the customer."""
    if not Booking_id:
           return "Atleast one value is missing"
    query=food_orders.where("Booking_id",'==', Booking_id)
    results=query.stream()
    output=[]

    for details in results:
        output.append(details.to_dict())
    if len(output)==0:
         return "None orders popped up!"
    return output


def delete_food_order(Order_id:str)->bool:
    """ Deletes food order from the database on the basis of the Order id.
        Args:
            Order_id: (str) The Order id of the order 
        Returns: 
            True or False based on the success of the deletion."""
    if not Order_id :
            return "Atleast one value is missing"
    try:
        query=food_orders.where("Order_id",'==',Order_id)
        results=query.stream()

        for order in results:
            order.reference.delete()
        return True
    except:
        return False



def delete_grievances(Complaint_id:str)->bool:
    """ Deletes  Grievances on the basis of complaint_id.
        Args:
            Complaint_id: (str) The complaint_id of the complaint to be deleted.
        Returns:
            True or False based on the success of the deletion."""
    if not Complaint_id:
        return "Atleast one value is missing"
    try:
        query=grievances.where("Complaint_id",'==',Complaint_id)
        results=query.stream()
        for details in results:
            details.reference.delete()
        return True
    except:
        return False