from django.db import models
from django.utils import timezone
from datetime import timedelta

class Student(models.Model):
    rollno = models.BigIntegerField(primary_key=True)  # Changed to BigIntegerField for PostgreSQL
    name = models.CharField(max_length=50)
    fname = models.CharField(max_length=50)
    mname = models.CharField(max_length=50)
    gender = models.CharField(max_length=6)
    address = models.TextField()
    program = models.ForeignKey('adminapp.Program', on_delete=models.CASCADE)
    branch = models.ForeignKey('adminapp.Branch', on_delete=models.CASCADE)
    year = models.ForeignKey('adminapp.Year', on_delete=models.CASCADE)
    contactno = models.CharField(max_length=10)
    emailaddress = models.CharField(max_length=50)
    regdate = models.CharField(max_length=30)

    
    profile_photo = models.ImageField(
    upload_to='profile_photos/',
    blank=True,
    null=True
)
    def __str__(self):
        return f"{self.name} ({self.rollno})"

class Login(models.Model):
    userid = models.CharField(max_length=50, primary_key=True)
    password = models.CharField(max_length=30)
    confirmpassword = models.CharField(max_length=30)
    usertype = models.CharField(max_length=50)
    status = models.CharField(max_length=10)

# class Enquiry(models.Model):
#     name = models.CharField(max_length=50)
#     gender = models.CharField(max_length=6)
#     address = models.TextField()
#     contactno = models.CharField(max_length=10)
#     emailaddress = models.CharField(max_length=50)
#     enquirytext = models.TextField()
#     enquirydate = models.CharField(max_length=30)

# For forgot password / reset password token
class PasswordResetToken(models.Model):
    userid = models.CharField(max_length=50)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
        
    def is_expired(self):
        expiry_time = self.created_at + timedelta(hours=1)  # 1 hour expiry
        return timezone.now() > expiry_time
        
    def __str__(self):
        return f"Reset token for {self.userid}"
    
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    # Basic fields
    name = models.CharField(max_length=100)
    emailaddress = models.CharField(max_length=50)  # Changed from 'email' to match Student
    contactno = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    
    # New fields
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enquiries', null=True, blank=True)
    subject = models.CharField(max_length=200, default='General Enquiry')
    message = models.TextField(default='')
    enquirytext = models.TextField(blank=True)  # Keep for backward compatibility
    enquirydate = models.CharField(max_length=30, blank=True)  # Keep for backward compatibility
    category = models.CharField(max_length=100, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        verbose_name_plural = "Enquiries"
        ordering = ['-id']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
# ADD THIS MODEL - It was missing!
class EnquiryReply(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Enquiry Replies"
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply by {self.user.username} on {self.enquiry.subject}"    
class Book(models.Model):

    title = models.CharField(max_length=200)

    author = models.CharField(
        max_length=150,
        blank=True
    )

    category = models.CharField(
        max_length=100,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    file = models.FileField(
        upload_to='ebooks/'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.title
class AssessmentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField(default=5)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.score}/{self.total}"
class CourseProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey('adminapp.Course', on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.name} - {self.course.title} - {self.progress}%"
class Lesson(models.Model):

    course = models.ForeignKey(
        'adminapp.Course',
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    order = models.IntegerField(
        default=1
    )

    def __str__(self):

        return f"{self.course.title} - {self.title}"
class LessonProgress(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE
    )

    completed = models.BooleanField(
        default=False
    )

    def __str__(self):

        return f"{self.student.name} - {self.lesson.title}"