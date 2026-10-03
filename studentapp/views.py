
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import FileResponse
from django.db.models import Q
from datetime import datetime
import os

from .models import StuResponse, Question, Answer

from adminapp.models import (
    Material,
    Course,
    Program,
    Branch,
    Year,
    NewsAnnouncement,
    NewsCategory
)

from nouapp.models import (
    Student,
    Login,
    Enquiry,
    EnquiryReply
)


# =========================================================
# NEWS HELPER
# =========================================================

def get_available_news():

    now = datetime.now()

    news = NewsAnnouncement.objects.filter(
        is_active=True
    )

    news = news.filter(
        Q(publish_date__isnull=True) |
        Q(publish_date__lte=now)
    )

    news = news.filter(
        Q(expiry_date__isnull=True) |
        Q(expiry_date__gte=now)
    )

    return news.order_by(
        '-is_pinned',
        '-priority',
        '-publish_date'
    )


# =========================================================
# STUDENT HOME / DASHBOARD
# =========================================================

@cache_control(
    no_cache=True,
    must_revalidate=True,
    no_store=True
)
def studenthome(request):

    # -----------------------------------------------------
    # CHECK LOGIN
    # -----------------------------------------------------

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    # -----------------------------------------------------
    # GET STUDENT
    # -----------------------------------------------------

    try:

        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    # =====================================================
    # GREETING
    # =====================================================

    current_hour = datetime.now().hour

    if 5 <= current_hour < 12:

        greeting = "Good Morning"
        greeting_icon = "🌅"
        greeting_message = (
            "Have a great day and keep learning!"
        )

    elif 12 <= current_hour < 17:

        greeting = "Good Afternoon"
        greeting_icon = "☀️"
        greeting_message = (
            "Hope you are having a productive day!"
        )

    else:

        greeting = "Good Evening"
        greeting_icon = "🌙"
        greeting_message = (
            "Keep learning and achieve your goals!"
        )

    # =====================================================
    # STUDENT NAME
    # =====================================================

    student_name = student.name

    # =====================================================
    # STUDY MATERIALS
    # =====================================================

    materials = Material.objects.filter(
        is_public=True
    )

    material_count = materials.count()

    latest_material = materials.select_related(
        'course',
        'category'
    ).order_by(
        '-created_at'
    ).first()

    # =====================================================
    # QUESTIONS
    # =====================================================

    question_count = Question.objects.count()

    # =====================================================
    # ANSWERS
    # =====================================================

    answer_count = Answer.objects.count()

    # =====================================================
    # NEWS
    # =====================================================

    available_news = get_available_news().select_related(
        'category'
    )

    news_count = available_news.count()

    recent_news = available_news[:5]

    # =====================================================
    # STUDENT ENQUIRIES
    # =====================================================

    student_enquiries = Enquiry.objects.filter(
        emailaddress=student.emailaddress
    )

    enquiry_count = student_enquiries.count()

    pending_enquiries = student_enquiries.filter(
        status='pending'
    ).count()

    # =====================================================
    # STUDENT ACTIVITY
    # =====================================================

    student_question_count = Question.objects.filter(
        postedby=student.name
    ).count()

    student_answer_count = Answer.objects.filter(
        answered=student.name
    ).count()

    student_enquiry_count = student_enquiries.count()

    # =====================================================
    # ENGAGEMENT SCORE
    # =====================================================

    engagement_score = (
        student_question_count
        + student_answer_count
        + student_enquiry_count
    )

    # =====================================================
    # DASHBOARD CONTEXT
    # =====================================================

    context = {

        # -------------------------------------------------
        # STUDENT
        # -------------------------------------------------

        'stu': student,
        'student': student,
        'student_name': student_name,

        # -------------------------------------------------
        # GREETING
        # -------------------------------------------------

        'greeting': greeting,
        'greeting_icon': greeting_icon,
        'greeting_message': greeting_message,

        # -------------------------------------------------
        # COUNTS
        # -------------------------------------------------

        'material_count': material_count,
        'question_count': question_count,
        'answer_count': answer_count,
        'news_count': news_count,
        'enquiry_count': enquiry_count,

        # Alternative names
        'materials_count': material_count,
        'questions_count': question_count,
        'answers_count': answer_count,
        'announcements_count': news_count,
        'enquiries_count': enquiry_count,

        # -------------------------------------------------
        # LATEST MATERIAL
        # -------------------------------------------------

        'latest_material': latest_material,

        # -------------------------------------------------
        # RECENT NEWS
        # -------------------------------------------------

        'recent_news': recent_news,

        # -------------------------------------------------
        # ENQUIRIES
        # -------------------------------------------------

        'pending_enquiries': pending_enquiries,

        # -------------------------------------------------
        # ENGAGEMENT
        # -------------------------------------------------

        'engagement_score': engagement_score,

        # -------------------------------------------------
        # STUDENT ACTIVITY
        # -------------------------------------------------

        'student_question_count': student_question_count,
        'student_answer_count': student_answer_count,
        'student_enquiry_count': student_enquiry_count,
    }

    # =====================================================
    # OPEN DASHBOARD
    # =====================================================

    return render(
        request,
        'studenthome.html',
        context
    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

def studentlogout(request):

    request.session.flush()

    return redirect('nouapp:login')


# =========================================================
# STUDENT RESPONSE / FEEDBACK
# =========================================================

def response(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    if request.method == 'POST':

        try:

            StuResponse.objects.create(
                rollno=student.rollno,
                name=student.name,
                program=student.program,
                branch=student.branch,
                year=student.year,
                contactno=student.contactno,
                emailaddress=student.emailaddress,
                responsetype=request.POST.get(
                    'responsetype',
                    ''
                ),
                subject=request.POST.get(
                    'subject',
                    ''
                ),
                responsetext=request.POST.get(
                    'responsetext',
                    ''
                ),
                responsedate=datetime.now().date()
            )

            messages.success(
                request,
                "Response submitted successfully."
            )

            return redirect(
                'studentapp:studenthome'
            )

        except Exception as e:

            print(
                "Response error:",
                e
            )

            messages.error(
                request,
                "Unable to submit response."
            )

    return render(
        request,
        'response.html',
        {
            'stu': student,
            'student': student,
        }
    )


# =========================================================
# POST QUESTION
# =========================================================

def postquestion(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    if request.method == 'POST':

        question_text = request.POST.get(
            'question',
            ''
        ).strip()

        if not question_text:

            messages.error(
                request,
                "Please enter a question."
            )

        else:

            try:

                Question.objects.create(
                    question=question_text,
                    postedby=student.name,
                    posteddate=datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                messages.success(
                    request,
                    "Question posted successfully."
                )

                return redirect(
                    'studentapp:postans'
                )

            except Exception as e:

                print(
                    "Post question error:",
                    e
                )

                messages.error(
                    request,
                    "Unable to post question."
                )

    return render(
        request,
        'postquestion.html',
        {
            'student': student,
            'stu': student,
        }
    )


# =========================================================
# POST ANSWER
# =========================================================

def postanswer(request, qid):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    question = get_object_or_404(
        Question,
        qid=qid
    )

    try:

        student = Student.objects.get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    if request.method == 'POST':

        answer_text = request.POST.get(
            'answer',
            ''
        ).strip()

        if not answer_text:

            messages.error(
                request,
                "Please enter an answer."
            )

            return render(
                request,
                'postanswer.html',
                {
                    'question': question,
                    'student': student,
                    'stu': student,
                }
            )

        try:

            Answer.objects.create(
                answer=answer_text,
                answered=student.name,
                posteddate=datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                qid=question.qid
            )

            messages.success(
                request,
                "Answer posted successfully."
            )

            return redirect(
                'studentapp:viewanswer',
                qid=question.qid
            )

        except Exception as e:

            print(
                "POST ANSWER ERROR:",
                e
            )

            messages.error(
                request,
                "Unable to post answer: " + str(e)
            )

    return render(
        request,
        'postanswer.html',
        {
            'question': question,
            'student': student,
            'stu': student,
        }
    )


# =========================================================
# SHOW QUESTIONS
# =========================================================

def postans(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    questions = Question.objects.all().order_by(
        '-qid'
    )

    return render(
        request,
        'postans.html',
        {
            'questions': questions,
            'student': student,
            'stu': student,
        }
    )


# =========================================================
# VIEW ANSWERS
# =========================================================

def viewanswer(request, qid):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    question = get_object_or_404(
        Question,
        qid=qid
    )

    answers = Answer.objects.filter(
        qid=question.qid
    ).order_by(
        '-aid'
    )

    return render(
        request,
        'viewanswer.html',
        {
            'question': question,
            'answers': answers,
        }
    )


# =========================================================
# VIEW PROFILE + PROFILE PHOTO UPLOAD
# =========================================================

def viewprofile(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(
            rollno=rollno
        )

        if request.method == 'POST':

            profile_photo = request.FILES.get(
                'profile_photo'
            )

            if not profile_photo:

                messages.error(
                    request,
                    "Please select a photo."
                )

            else:

                allowed_types = [
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/webp'
                ]

                if profile_photo.content_type not in allowed_types:

                    messages.error(
                        request,
                        "Please upload JPG, JPEG, PNG or WEBP image."
                    )

                elif profile_photo.size > 5 * 1024 * 1024:

                    messages.error(
                        request,
                        "Photo size must be less than 5 MB."
                    )

                else:

                    if student.profile_photo:

                        try:

                            old_photo_path = student.profile_photo.path

                            if os.path.exists(old_photo_path):

                                os.remove(
                                    old_photo_path
                                )

                        except Exception as e:

                            print(
                                "Old photo delete error:",
                                e
                            )

                    student.profile_photo = profile_photo

                    student.save(
                        update_fields=[
                            'profile_photo'
                        ]
                    )

                    messages.success(
                        request,
                        "Profile photo updated successfully!"
                    )

                    return redirect(
                        'studentapp:viewprofile'
                    )

        return render(
            request,
            'viewprofile.html',
            {
                'stu': student,
                'student': student,
            }
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect(
            'nouapp:login'
        )


# =========================================================
# CHANGE PASSWORD
# =========================================================

def changepassword(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

        login_user = Login.objects.get(
            userid=str(rollno)
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    except Login.DoesNotExist:

        messages.error(
            request,
            "Login account not found."
        )

        return redirect('nouapp:login')

    if request.method == 'POST':

        oldpassword = request.POST.get(
            'oldpassword',
            ''
        )

        newpassword = request.POST.get(
            'newpassword',
            ''
        )

        confirmpassword = request.POST.get(
            'confirmpassword',
            ''
        )

        if login_user.password != oldpassword:

            messages.error(
                request,
                "Old password is incorrect."
            )

        elif newpassword != confirmpassword:

            messages.error(
                request,
                "New passwords do not match."
            )

        elif not newpassword:

            messages.error(
                request,
                "Please enter a new password."
            )

        else:

            login_user.password = newpassword
            login_user.confirmpassword = confirmpassword

            login_user.save()

            messages.success(
                request,
                "Password changed successfully."
            )

            return redirect(
                'studentapp:studenthome'
            )

    return render(
        request,
        'changepassword.html',
        {
            'stu': student,
            'student': student,
        }
    )


# =========================================================
# VIEW STUDY MATERIALS
# =========================================================

def viewmat(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect('nouapp:login')

    materials = Material.objects.filter(
        is_public=True
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'viewmat.html',
        {
            'materials': materials,
            'material_count': materials.count(),

            'program': student.program,
            'branch': student.branch,
            'year': student.year,

            'stu': student,
            'student': student,
        }
    )


# =========================================================
# DOWNLOAD MATERIAL
# =========================================================

def download_material(request, material_id):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    material = get_object_or_404(
        Material,
        id=material_id
    )

    try:

        material.download_count += 1

        material.save(
            update_fields=[
                'download_count'
            ]
        )

    except Exception:

        pass

    try:

        return FileResponse(
            material.file.open('rb'),
            as_attachment=True,
            filename=material.file.name.split('/')[-1]
        )

    except Exception as e:

        print(
            "Download error:",
            e
        )

        messages.error(
            request,
            "Unable to download material."
        )

        return redirect(
            'studentapp:viewmat'
        )


# =========================================================
# STUDENT NEWS
# =========================================================

def student_news(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(
            rollno=rollno
        )

        news = get_available_news().select_related(
            'category'
        )

        current_category = request.GET.get(
            'category',
            ''
        ).strip()

        if current_category:

            news = news.filter(
                category_id=current_category
            )

        categories = NewsCategory.objects.all().order_by(
            'name'
        )

        context = {

            'stu': student,
            'student': student,

            'news_list': news,
            'news': news,
            'announcements': news,

            'news_count': news.count(),

            'categories': categories,
            'current_category': current_category,
        }

        return render(
            request,
            'student_news.html',
            context
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect(
            'nouapp:login'
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        messages.error(
            request,
            "Unable to load news."
        )

        return redirect(
            'studentapp:studenthome'
        )


# =========================================================
# STUDENT ENQUIRY DASHBOARD
# =========================================================

def student_enquiry_dashboard(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

        enquiries = Enquiry.objects.filter(
            emailaddress=student.emailaddress
        ).order_by(
            '-id'
        )

        return render(
            request,
            'student_enquiry_dashboard.html',
            {
                'stu': student,
                'student': student,
                'enquiries': enquiries,
            }
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect(
            'nouapp:login'
        )


# =========================================================
# CREATE ENQUIRY
# =========================================================

def create_enquiry(request):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect(
            'nouapp:login'
        )

    if request.method == 'POST':

        subject = request.POST.get(
            'subject',
            ''
        ).strip()

        message = request.POST.get(
            'message',
            ''
        ).strip()

        category = request.POST.get(
            'category',
            ''
        ).strip()

        priority = request.POST.get(
            'priority',
            'low'
        ).strip()

        if not subject:

            messages.error(
                request,
                "Please enter the enquiry subject."
            )

        elif not message:

            messages.error(
                request,
                "Please enter the enquiry message."
            )

        else:

            try:

                enquiry = Enquiry.objects.create(

                    name=student.name,

                    emailaddress=student.emailaddress,

                    contactno=student.contactno,

                    address=student.address,

                    subject=subject,

                    message=message,

                    enquirytext=message,

                    enquirydate=datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    category=category,

                    priority=priority,

                    status='pending',

                    student=None
                )

                messages.success(
                    request,
                    "Enquiry submitted successfully."
                )

                return redirect(
                    'studentapp:enquiry_detail',
                    enquiry_id=enquiry.id
                )

            except Exception as e:

                print(
                    "Create enquiry error:",
                    e
                )

                messages.error(
                    request,
                    "Unable to submit enquiry."
                )

    return render(
        request,
        'create_enquiry.html',
        {
            'stu': student,
            'student': student,
        }
    )


# =========================================================
# ENQUIRY DETAIL + STUDENT REPLY
# =========================================================

def enquiry_detail(request, enquiry_id):

    if request.session.get('rollno') is None:
        return redirect('nouapp:login')

    rollno = request.session.get('rollno')

    try:

        student = Student.objects.get(
            rollno=rollno
        )

        # -------------------------------------------------
        # GET ENQUIRY
        # -------------------------------------------------

        enquiry = get_object_or_404(
            Enquiry,
            id=enquiry_id,
            emailaddress=student.emailaddress
        )

        # -------------------------------------------------
        # STUDENT REPLY
        # -------------------------------------------------

        if request.method == 'POST':

            reply_message = request.POST.get(
                'reply_message',
                ''
            ).strip()

            if not reply_message:

                messages.error(
                    request,
                    "Please enter your reply."
                )

            elif enquiry.status == 'resolved':

                messages.warning(
                    request,
                    "This enquiry has already been resolved."
                )

            elif enquiry.status == 'closed':

                messages.warning(
                    request,
                    "This enquiry has been closed."
                )

            else:

                try:

                    username = f"student_{student.rollno}"

                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': student.name,
                            'email': student.emailaddress,
                        }
                    )

                    if user.first_name != student.name:

                        user.first_name = student.name

                    if user.email != student.emailaddress:

                        user.email = student.emailaddress

                    user.save()

                    EnquiryReply.objects.create(
                        enquiry=enquiry,
                        user=user,
                        message=reply_message,
                        is_admin=False
                    )

                    if enquiry.status == 'pending':

                        enquiry.status = 'in_progress'

                        enquiry.save(
                            update_fields=[
                                'status'
                            ]
                        )

                    messages.success(
                        request,
                        "Your reply has been sent successfully."
                    )

                    return redirect(
                        'studentapp:enquiry_detail',
                        enquiry_id=enquiry.id
                    )

                except Exception as e:

                    print(
                        "Student reply error:",
                        e
                    )

                    messages.error(
                        request,
                        "Unable to send your reply."
                    )

        # -------------------------------------------------
        # GET REPLIES
        # -------------------------------------------------

        replies = EnquiryReply.objects.filter(
            enquiry=enquiry
        ).select_related(
            'user'
        ).order_by(
            'created_at'
        )

        # -------------------------------------------------
        # DISPLAY PAGE
        # -------------------------------------------------

        return render(
            request,
            'enquiry_detail.html',
            {
                'stu': student,
                'student': student,
                'enquiry': enquiry,
                'replies': replies,
            }
        )

    except Student.DoesNotExist:

        messages.error(
            request,
            "Student profile not found."
        )

        return redirect(
            'nouapp:login'
        )
