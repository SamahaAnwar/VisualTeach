import os
from pymongo import MongoClient
from PIL import Image
from io import BytesIO
from datetime import datetime

class TeacherDatabase:
    def __init__(self, db_name='visualTeach_db', counter_collection='teacher_counter'):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.counter_collection = self.db[counter_collection]

    def get_next_teacher_count(self, sequence_name):
        # Find and modify the counter document
        sequence_document = self.counter_collection.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {'count': 1}},
            upsert=True,  # Create the document if it doesn't exist
            return_document=True
        )

        # Return the sequence value
        return sequence_document['count']

    def addProfilePic(self, image_path):
        with open(image_path, 'rb') as image_file:
            image_data = BytesIO(image_file.read())

            # Create a PIL Image object
            pil_image = Image.open(image_data)

            # Convert PIL Image to bytes for storage in MongoDB
            image_bytes = BytesIO()
            pil_image.save(image_bytes, format='JPEG')  
            return image_bytes
        
    def get_employee_id(self, id):
        return "T"+str(id)

    def add_teacher(self, name, password, age, email, img= "D:\\FYP\\FYP Database\\teacher_pfp\\avatar.jpg"):
        id = self.get_next_teacher_count("teacher_counter")
        teacher_collection = self.db['Teacher']
        employee_id = self.get_employee_id(id)
        profilePic = self.addProfilePic(image_path=img).getvalue()
        teacher_collection.insert_one({
        "_id": id,
        "name": name,
        "employeeID": employee_id,
        "password": password,
        "age": age,
        "email": email,
        "profilePic": profilePic
        })

        return employee_id
 

     
class StudentDatabase:
    def __init__(self, db_name='visualTeach_db', counter_collection='student_counter'):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
        self.counter_collection = self.db[counter_collection]

    def get_next_student_count(self, sequence_name):
        # Find and modify the counter document
        sequence_document = self.counter_collection.find_one_and_update(
            {'_id': sequence_name},
            {'$inc': {'count': 1}},
            upsert=True,  # Create the document if it doesn't exist
            return_document=True
        )

        # Return the sequence value
        return sequence_document['count']

    def addProfilePic(self, image_path):
        with open(image_path, 'rb') as image_file:
            image_data = BytesIO(image_file.read())

            # Create a PIL Image object
            pil_image = Image.open(image_data)

            # Convert PIL Image to bytes for storage in MongoDB
            image_bytes = BytesIO()
            pil_image.save(image_bytes, format='JPEG')  
            return image_bytes
        
    def get_student_id(self, id):
        return "S"+str(id)

    def add_student(self, name, password, age, email, img= "D:\\FYP\\FYP Database\\student_pfp\\student3.jpg"):
        id = self.get_next_student_count("student_counter")
        student_collection = self.db['student']
        student_id = self.get_student_id(id)
        profilePic = self.addProfilePic(image_path=img).getvalue()
        student_collection.insert_one({
        "_id": id,
        "name":name,
        "studentID": student_id,
        "password": password,
        "age": age,
        "email": email,
        "profilePic": profilePic
        })

        return student_id
    

class ClassDatabase:
    def __init__(self, db_name='visualTeach_db'):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]
       
    def add_class(self, class_id, class_name):
        class_collection = self.db['class']  
        class_collection.insert_one({
        "classID":class_id,
        "className": class_name
        })

        return class_id 

class Canvas:
    def __init__(self, db_name='visualTeach_db'):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]

    def addCanvas(self, canvas_img, title = "untitled"):
        canvas_collection = self.db['canvas']
        canvas_data = BytesIO(canvas_img.read())
        # Create a PIL Image object
        pil_image = Image.open(canvas_data)

        # Convert PIL Image to bytes for storage in MongoDB
        image_bytes = BytesIO()
        pil_image.save(image_bytes, format='JPEG')
        canvas_collection.insert_one({
        "title": title,
        "canvas": image_bytes.getvalue(),
        "timestamp": { "$currentDate": { "$type": "date" } }
        })

    #Finding Canvas on the basis of time or title
    def findCanvas(self, title, date):
        canvas_collection = self.db['canvas']
        canvas_collection.find({
        "$or": [
            { "title": title },
            { "timestamp": { "$gte": datetime(date) } }
            ]
        })

    def updateCanvas(self, title, canvas_img):
        canvas_collection = self.db['canvas']

        pil_image = Image.open(canvas_img)

        # Convert PIL Image to bytes for storage in MongoDB
        image_bytes = BytesIO()
        pil_image.save(image_bytes, format='JPEG')
        #if the canvas has same title
        if title is not None:
            canvas_collection.updateMany({
                {"title": title},
                {"$set":{"canvas": image_bytes.getvalue()}}
            })

class Session:
    def __init__(self, db_name='visualTeach_db'):
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[db_name]


#MAIN
canvas_db = Canvas()
canvas_path = "C:\\Users\\Windows 10 Pro\\Downloads\\drawing.png"
 # Read image file
with open(canvas_path, 'rb') as image_file:
    image_data = BytesIO(image_file.read())


canvas_db.addCanvas(image_data, "test")
 
     


