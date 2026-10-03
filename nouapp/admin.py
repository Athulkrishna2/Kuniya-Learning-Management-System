from django.contrib import admin
from .models import Book
from . models import Student, Login, Enquiry
from .models import CourseProgress, Lesson,LessonProgress


# Register your models here.

admin.site.register(Student)
admin.site.register(Login)
admin.site.register(Enquiry)
admin.site.register(Book)
admin.site.register(CourseProgress)
admin.site.register(Lesson)
admin.site.register(LessonProgress)