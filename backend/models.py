from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)  # Added image field

    def __str__(self):
        return self.name
#{
#    "name": "Bsc-csit",
#    "description": "Its all about the Bachelor of science in computer science and information technology..",
#    "image": null
#}
class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="semesters")
    number = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ("course", "number")  #Ensures semesters are unique per course
        
    def __str__(self):
        return f"Semester {self.number} - {self.course.name}"

#{
#    "course": 1,
#    "number": 1,
#    "description": "This is the first semester of the Bsc-csit course."
#}

class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE,related_name="subjects")  # Foreign key reference to Semester
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ("semester", "code")  #Ensures semesters are unique per course

    def __str__(self):
        return f"{self.name} (Sem {self.semester.number})"
    
#{
#    "semester": 1,  (id of semester)
#    "name": "Object-Oriented Programming",
#    "code": "CSIT201",
#    "credits": 3,
#    "description": "This course covers object-oriented programming concepts using C++."
#}

class PastQuestion(models.Model):
    subject = models.ForeignKey(Subject, related_name="past_questions", on_delete=models.CASCADE)
    year = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='past_questions/',null=True, blank=True)  # File upload for the past question papers

    class Meta:
        unique_together = ("subject", "year") 
    
    def __str__(self):
        return f"Past Question {self.year} - {self.title}"

class Syllabus(models.Model):
    subject = models.OneToOneField(Subject, on_delete=models.CASCADE, related_name="syllabus")
    objectives = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='syllabus_files/', null=True, blank=True)  # File upload for the syllabus
    def __str__(self):
        return f"Syllabus of {self.subject.name}"

class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="chapters")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField()  # Helps in ordering chapters

    class Meta:
        ordering = ["order"]
        unique_together = ("subject", "order") 

    def __str__(self):
        return f"{self.title} - {self.subject.name}"    
    
class Note(models.Model):
    chapter = models.ForeignKey(Chapter, related_name="notes", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='notes/')  # File upload for the notes
    
    class Meta:
        unique_together = ("chapter", "title") 
    
    def __str__(self):
        return self.title
    

    


