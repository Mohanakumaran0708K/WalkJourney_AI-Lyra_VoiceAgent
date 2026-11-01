class Detection: 
    def __init__(self, object_id, class_name, confidence):
        self.object_id = object_id
        self.class_name = class_name
        self.confidence = confidence

person=Detection(1, "person", 0.95)

class Detection:
    
    def __init__(self, object_id, class_name, confidence):

        self.object_id = object_id
        self.class_name = class_name
        self.confidence = confidence


person = Detection(1, "person", 0.95)

print("Object ID:", person.object_id)
print("Object:", person.class_name)
print("Confidence:", person.confidence)