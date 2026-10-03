from django.shortcuts import render, redirect, reverse
from adminapp.models import Course, Program, Branch, Year, News

from .models import (
    Enquiry,
    Student,
    Login,
    Book,
    AssessmentResult,
    CourseProgress
)

from datetime import date

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from . import smssender
from django.db.models import Q
from django.core.paginator import Paginator

from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods

from django.views.decorators.csrf import (
    csrf_exempt,
    ensure_csrf_cookie
)

from django.views.decorators.cache import never_cache

import json
import uuid

from .chatbot_logic import chatbot


# =========================================================
# CHAT API
# =========================================================

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):

    try:

        data = json.loads(request.body)

        user_message = data.get('message', '').strip()

        if not user_message:

            return JsonResponse(
                {'error': 'Empty message'},
                status=400
            )

        bot_response, tag = chatbot.get_response(
            user_message
        )

        return JsonResponse(
            {
                'response': bot_response,
                'tag': tag
            }
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {'error': 'Invalid JSON'},
            status=400
        )

    except Exception as e:

        return JsonResponse(
            {
                'error': 'Server error',
                'details': str(e)
            },
            status=500
        )


# =========================================================
# THEME
# =========================================================

@require_POST
def set_theme(request):

    theme = request.POST.get(
        'theme',
        'light'
    )

    request.session['theme'] = theme

    return JsonResponse(
        {'status': 'ok'}
    )


# =========================================================
# HOME PAGE
# =========================================================

def index(request):

    ns = News.objects.all()

    return render(
        request,
        "index.html",
        locals()
    )


# =========================================================
# ABOUT US
# =========================================================

def aboutus(request):

    ns = News.objects.all()

    return render(
        request,
        "aboutus.html",
        locals()
    )


# =========================================================
# REGISTRATION
# =========================================================

def registration(request):

    if request.method == "POST":

        rollno = request.POST['rollno']
        name = request.POST['name']
        fname = request.POST['fatherName']
        mname = request.POST['motherName']
        gender = request.POST['gender']
        address = request.POST['address']

        program_id = request.POST['program']
        branch_id = request.POST['branch']
        year_id = request.POST['year']

        contactno = request.POST['contactNo']
        emailaddress = request.POST['emailAddress']
        password = request.POST['password']

        regdate = date.today()

        usertype = 'student'
        status = 'false'

        try:

            program_obj = Program.objects.get(
                id=program_id
            )

            branch_obj = Branch.objects.get(
                id=branch_id
            )

            year_obj = Year.objects.get(
                id=year_id
            )

            # Prevent duplicate registration

            if Student.objects.filter(
                rollno=rollno
            ).exists():

                messages.error(
                    request,
                    'This roll number is already registered.'
                )

            elif Login.objects.filter(
                userid=rollno
            ).exists():

                messages.error(
                    request,
                    'A login account already exists for this roll number.'
                )

            else:

                stu = Student(
                    rollno=rollno,
                    name=name,
                    fname=fname,
                    mname=mname,
                    gender=gender,
                    address=address,
                    program=program_obj,
                    branch=branch_obj,
                    year=year_obj,
                    contactno=contactno,
                    emailaddress=emailaddress,
                    regdate=regdate
                )

                log = Login(
                    userid=rollno,
                    password=password,
                    usertype=usertype,
                    status=status
                )

                stu.save()
                log.save()

                messages.success(
                    request,
                    'Your Registration is submitted'
                )

        except (
            Program.DoesNotExist,
            Branch.DoesNotExist,
            Year.DoesNotExist
        ):

            messages.error(
                request,
                'Invalid program, branch, or year selected'
            )

        except Exception as e:

            messages.error(
                request,
                f'Registration failed: {str(e)}'
            )

    program = Program.objects.all()
    branch = Branch.objects.all()
    year = Year.objects.all()
    ns = News.objects.all()

    return render(
        request,
        "registration.html",
        locals()
    )


# =========================================================
# LOGIN
# =========================================================

@never_cache
@ensure_csrf_cookie
def login(request):

    if request.method == "POST":

        userid = request.POST.get(
            'userid',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        usertype = request.POST.get(
            'usertype',
            ''
        ).strip().lower()

        if not userid or not password or not usertype:

            messages.error(
                request,
                'Please enter all login details.'
            )

        else:

            try:

                # -----------------------------------------
                # FIND LOGIN ACCOUNT
                # -----------------------------------------

                obj = Login.objects.get(
                    userid=userid
                )

                # -----------------------------------------
                # CHECK PASSWORD
                # -----------------------------------------

                if obj.password != password:

                    messages.error(
                        request,
                        'Invalid user ID or password.'
                    )

                # -----------------------------------------
                # CHECK USER TYPE
                # -----------------------------------------

                elif (
                    obj.usertype or ''
                ).strip().lower() != usertype:

                    messages.error(
                        request,
                        'Please select the correct user type.'
                    )

                # -----------------------------------------
                # STUDENT LOGIN
                # -----------------------------------------

                elif usertype == 'student':

                    student = Student.objects.get(
                        rollno=userid
                    )

                    # Store student session
                    request.session['rollno'] = (
                        student.rollno
                    )

                    request.session.modified = True

                    print(
                        "Student login successful:",
                        student.rollno
                    )

                    return redirect(
                        'studentapp:studenthome'
                    )

                # -----------------------------------------
                # ADMIN LOGIN
                # -----------------------------------------

                elif usertype == 'admin':

                    request.session['adminid'] = userid

                    request.session.modified = True

                    print(
                        "Admin login successful:",
                        userid
                    )

                    return redirect(
                        'adminapp:adminhome'
                    )

                else:

                    messages.error(
                        request,
                        'Invalid user type.'
                    )

            except Login.DoesNotExist:

                messages.error(
                    request,
                    'Invalid user ID or password.'
                )

            except Student.DoesNotExist:

                messages.error(
                    request,
                    'Student record not found.'
                )

            except Exception as e:

                print(
                    "Login error:",
                    e
                )

                messages.error(
                    request,
                    'Login failed. Please try again.'
                )

    ns = News.objects.all()

    return render(
        request,
        "login.html",
        {
            'ns': ns
        }
    )


# =========================================================
# CONTACT US
# =========================================================

def contactus(request):

    if request.method == "POST":

        name = request.POST['name']
        gender = request.POST['gender']
        address = request.POST['address']
        contactno = request.POST['contactno']
        emailaddress = request.POST['emailaddress']
        enquirytext = request.POST['enquirytext']

        enquirydate = date.today()

        enq = Enquiry(
            name=name,
            gender=gender,
            address=address,
            contactno=contactno,
            emailaddress=emailaddress,
            enquirytext=enquirytext,
            enquirydate=enquirydate
        )

        enq.save()

        messages.success(
            request,
            'Your Enquiry is submitted'
        )

    ns = News.objects.all()

    return render(
        request,
        "contactus.html",
        locals()
    )


# =========================================================
# COURSES
# =========================================================

def courses(request):

    courses = Course.objects.filter(
        is_active=True
    )

    return render(
        request,
        "courses.html",
        {
            "courses": courses
        }
    )


# =========================================================
# COURSE DETAILS
# =========================================================

def course_details(request, course_id):

    from .models import Lesson, LessonProgress

    course = Course.objects.get(
        id=course_id
    )

    lessons = Lesson.objects.filter(
        course=course
    ).order_by(
        'order'
    )

    rollno = request.session.get(
        'rollno'
    )

    progress = 0
    lesson_progress = []
    completed_lesson_ids = []

    if rollno:

        try:

            student = Student.objects.get(
                rollno=rollno
            )

            if request.method == "POST":

                action = request.POST.get(
                    'action'
                )

                # Start course

                if action == "start":

                    CourseProgress.objects.update_or_create(
                        student=student,
                        course=course,
                        defaults={
                            'progress': 0
                        }
                    )

                # Complete lesson

                elif action == "complete_lesson":

                    lesson_id = request.POST.get(
                        'lesson_id'
                    )

                    try:

                        lesson = Lesson.objects.get(
                            id=lesson_id,
                            course=course
                        )

                        LessonProgress.objects.update_or_create(
                            student=student,
                            lesson=lesson,
                            defaults={
                                'completed': True
                            }
                        )

                    except Lesson.DoesNotExist:

                        pass

                # Complete entire course

                elif action == "complete":

                    CourseProgress.objects.update_or_create(
                        student=student,
                        course=course,
                        defaults={
                            'progress': 100
                        }
                    )

            lesson_progress = LessonProgress.objects.filter(
                student=student,
                lesson__course=course,
                completed=True
            )

            completed_lesson_ids = list(
                lesson_progress.values_list(
                    'lesson_id',
                    flat=True
                )
            )

            completed_lessons = (
                lesson_progress.count()
            )

            total_lessons = lessons.count()

            if total_lessons > 0:

                progress = round(
                    (
                        completed_lessons /
                        total_lessons
                    ) * 100
                )

            else:

                progress_obj = (
                    CourseProgress.objects.filter(
                        student=student,
                        course=course
                    ).first()
                )

                if progress_obj:

                    progress = (
                        progress_obj.progress
                    )

            CourseProgress.objects.update_or_create(
                student=student,
                course=course,
                defaults={
                    'progress': progress
                }
            )

        except Student.DoesNotExist:

            pass

    return render(
        request,
        "course_details.html",
        {
            "course": course,
            "progress": progress,
            "lessons": lessons,
            "lesson_progress": lesson_progress,
            "completed_lesson_ids": completed_lesson_ids
        }
    )


# =========================================================
# SERVICES
# =========================================================

def services(request):

    return render(
        request,
        "services.html"
    )


# =========================================================
# LIBRARY
# =========================================================

def library(request):

    books = Book.objects.filter(
        is_active=True
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'library.html',
        {
            'books': books
        }
    )


# =========================================================
# RESET TOKENS
# =========================================================

reset_tokens = {}


# =========================================================
# FORGOT PASSWORD
# =========================================================

def forgot_password(request):

    if request.method == "POST":

        email = request.POST.get(
            "email"
        )

        try:

            student = Student.objects.get(
                emailaddress=email
            )

            if Login.objects.filter(
                userid=student.rollno
            ).exists():

                login_user = Login.objects.get(
                    userid=student.rollno
                )

                reset_token = str(
                    uuid.uuid4()
                )

                reset_tokens[
                    reset_token
                ] = login_user.userid

                reset_link = (
                    request.build_absolute_uri(
                        reverse(
                            'nouapp:reset_password',
                            args=[reset_token]
                        )
                    )
                )

                return render(
                    request,
                    "show_reset_link.html",
                    {
                        "reset_link": reset_link
                    }
                )

            else:

                messages.error(
                    request,
                    "No login found for this email"
                )

        except Student.DoesNotExist:

            messages.error(
                request,
                "Email not registered"
            )

    return render(
        request,
        "forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

def reset_password(request, token):

    if token not in reset_tokens:

        messages.error(
            request,
            "Invalid or expired link"
        )

        return render(
            request,
            "reset_password.html",
            {
                "token": token
            }
        )

    userid = reset_tokens[token]

    if request.method == 'POST':

        new_password = request.POST.get(
            'new_password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        if not new_password or not confirm_password:

            messages.error(
                request,
                "Please fill in both password fields"
            )

            return render(
                request,
                'reset_password.html',
                {
                    'token': token
                }
            )

        if len(new_password) > 30:

            messages.error(
                request,
                'Password cannot be longer than 30 characters'
            )

            return render(
                request,
                'reset_password.html',
                {
                    'token': token
                }
            )

        if new_password != confirm_password:

            messages.error(
                request,
                'Passwords do not match'
            )

            return render(
                request,
                'reset_password.html',
                {
                    'token': token
                }
            )

        try:

            login_user = Login.objects.get(
                userid=userid
            )

            login_user.password = new_password

            login_user.save()

            del reset_tokens[token]

            messages.success(
                request,
                "Password reset successfully! "
                "You can now login with your new password."
            )

            return redirect(
                'nouapp:login'
            )

        except Login.DoesNotExist:

            messages.error(
                request,
                'User not found'
            )

            return render(
                request,
                'reset_password.html',
                {
                    'token': token
                }
            )

    return render(
        request,
        "reset_password.html",
        {
            "token": token
        }
    )


# =========================================================
# SEARCH
# =========================================================

def search_view(request):

    query = request.GET.get(
        'q',
        ''
    ).strip()

    results = []

    message = ''

    if query:

        if query.isdigit():

            results = Student.objects.filter(
                Q(rollno=query)
                | Q(name__icontains=query)
                | Q(program__icontains=query)
                | Q(branch__icontains=query)
                | Q(contactno__icontains=query)
            ).distinct()

        else:

            results = Student.objects.filter(
                Q(name__icontains=query)
                | Q(program__icontains=query)
                | Q(branch__icontains=query)
                | Q(contactno__icontains=query)
            ).distinct()

        if not results.exists():

            message = (
                f"No results found for '{query}'."
            )

    else:

        message = (
            "Please enter a search term."
        )

    print(
        "Query:",
        query
    )

    print(
        "Results:",
        results
    )

    return render(
        request,
        'search_results.html',
        {
            'query': query,
            'results': results,
            'message': message
        }
    )


# =========================================================
# SCHEMA NORMALIZATION HELPERS
# =========================================================

def migrate_existing_students():

    from django.db import transaction

    from adminapp.models import (
        Program,
        Branch,
        Year
    )

    try:

        with transaction.atomic():

            students = Student.objects.all()

            for student in students:

                if isinstance(
                    student.program,
                    str
                ):

                    program_obj, created = (
                        Program.objects.get_or_create(
                            program=student.program
                        )
                    )

                    if created:

                        print(
                            f"Created Program: "
                            f"{student.program}"
                        )

            print(
                "Migration completed successfully"
            )

    except Exception as e:

        print(
            f"Error during migration: {e}"
        )


# =========================================================
# ENSURE DROPDOWN DATA
# =========================================================

def ensure_dropdown_data():

    from adminapp.models import (
        Program,
        Branch,
        Year
    )

    if not Program.objects.exists():

        programs = [
            'BCA',
            'MCA',
            'B.Tech',
            'M.Tech',
            'MBA'
        ]

        for prog in programs:

            Program.objects.create(
                program=prog
            )

    if not Branch.objects.exists():

        branches = [
            'Computer Science',
            'Electronics',
            'Mechanical',
            'Civil'
        ]

        for branch in branches:

            Branch.objects.create(
                branch=branch
            )

    if not Year.objects.exists():

        years = [
            '1st Year',
            '2nd Year',
            '3rd Year',
            '4th Year'
        ]

        for year in years:

            Year.objects.create(
                year=year
            )


# =========================================================
# CUSTOM 404
# =========================================================

def custom_404_view(
    request,
    exception
):

    return render(
        request,
        "404.html",
        status=404
    )


# =========================================================
# RESOURCES
# =========================================================

def resources(request):

    ns = News.objects.all()

    return render(
        request,
        "resources.html",
        locals()
    )


# =========================================================
# FAQS
# =========================================================

def faqs(request):

    return render(
        request,
        'faqs.html'
    )


# =========================================================
# ASSESSMENT
# =========================================================

def assessment(request):

    score = None

    if request.method == 'POST':

        correct_answers = {
            'q1': 'a',
            'q2': 'b',
            'q3': 'a',
            'q4': 'b',
            'q5': 'b',
        }

        score = 0

        for question, answer in correct_answers.items():

            if request.POST.get(question) == answer:

                score += 1

        rollno = request.session.get(
            'rollno'
        )

        if rollno:

            try:

                student = Student.objects.get(
                    rollno=rollno
                )

                AssessmentResult.objects.create(
                    student=student,
                    score=score,
                    total=5
                )

            except Student.DoesNotExist:

                pass

    return render(
        request,
        'assessment.html',
        {
            'score': score
        }
    )


# =========================================================
# PERFORMANCE
# =========================================================

def performance(request):

    if request.session.get(
        'rollno'
    ) is None:

        return redirect(
            'nouapp:login'
        )

    rollno = request.session.get(
        'rollno'
    )

    try:

        student = Student.objects.get(
            rollno=rollno
        )

        courses = Course.objects.filter(
            is_active=True
        )

        result = AssessmentResult.objects.filter(
            student=student
        ).order_by(
            '-date'
        ).first()

        if result:

            score = result.score

        else:

            score = 0

        course_progress = CourseProgress.objects.filter(
            student=student
        )

        courses_data = []

        for course in courses:

            progress_obj = course_progress.filter(
                course=course
            ).first()

            if progress_obj:

                course_progress_value = (
                    progress_obj.progress
                )

            else:

                course_progress_value = 0

            courses_data.append(
                {
                    'course': course,
                    'progress': course_progress_value
                }
            )

        courses_count = courses.count()

        if course_progress.exists():

            progress = round(
                sum(
                    item.progress
                    for item in course_progress
                )
                / course_progress.count()
            )

        else:

            progress = 0

        return render(
            request,
            'performance.html',
            {
                'student': student,
                'courses': courses,
                'courses_data': courses_data,
                'score': score,
                'progress': progress,
                'courses_count': courses_count,
            }
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            'Student profile not found'
        )

        return redirect(
            'nouapp:login'
        )