
# adminapp/analytics_utils.py

from django.db.models import Count, Q, F
from django.utils import timezone
from datetime import timedelta

from nouapp.models import Student
from studentapp.models import StuResponse, Question, Answer

from .models import (
    Material,
    News,
    StudentActivity,
    DailyStats,
    ProgramStats,
    BranchStats,
    Course,
    Program,
    Branch,
    Year
)


# ============================================================
# STUDENT ACTIVITY
# ============================================================

def log_student_activity(
    rollno,
    activity_type,
    request,
    additional_info=''
):
    """
    Log student activity.

    rollno:
        Student roll number

    activity_type:
        Example: login, logout, material_view,
        material_download, question_post, answer_post

    request:
        Django request object

    additional_info:
        Optional extra information
    """

    try:
        student = Student.objects.select_related(
            'program',
            'branch',
            'year'
        ).get(rollno=rollno)

        # Get IP address
        ip_address = request.META.get(
            'HTTP_X_FORWARDED_FOR',
            request.META.get('REMOTE_ADDR', '')
        )

        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()

        # Create activity
        StudentActivity.objects.create(
            rollno=rollno,
            student_name=student.name,
            program=student.program,
            branch=student.branch,
            year=student.year,
            activity_type=activity_type,
            ip_address=ip_address,
            additional_info=additional_info
        )

        print(
            f"Activity logged successfully: "
            f"{rollno} - {activity_type}"
        )

    except Student.DoesNotExist:
        print(
            f"Student with rollno {rollno} "
            f"not found for activity logging"
        )

    except Exception as e:
        print(
            f"Error logging student activity: {e}"
        )


# ============================================================
# ENROLLMENT ANALYTICS
# ============================================================

def get_enrollment_analytics(days=30):
    """
    Get enrollment and login analytics.
    """

    # Enrollment by program
    enrollment_by_program = Student.objects.values(
        'program'
    ).annotate(
        count=Count('rollno')
    ).order_by('-count')

    # Enrollment by branch
    enrollment_by_branch = Student.objects.values(
        'branch'
    ).annotate(
        count=Count('rollno')
    ).order_by('-count')

    # Enrollment by year
    enrollment_by_year = Student.objects.values(
        'year'
    ).annotate(
        count=Count('rollno')
    ).order_by('-count')

    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    daily_logins = []

    current_date = start_date

    while current_date <= end_date:

        login_count = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='login'
        ).count()

        unique_students = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='login'
        ).values(
            'rollno'
        ).distinct().count()

        daily_logins.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'logins': login_count,
            'unique_students': unique_students
        })

        current_date += timedelta(days=1)

    return {
        'enrollment_by_program': list(
            enrollment_by_program
        ),

        'enrollment_by_branch': list(
            enrollment_by_branch
        ),

        'enrollment_by_year': list(
            enrollment_by_year
        ),

        'daily_logins': daily_logins,

        'total_students': Student.objects.count()
    }


# ============================================================
# MATERIAL ANALYTICS
# ============================================================

def get_material_analytics(days=30):
    """
    Get study material usage analytics.
    """

    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)

    daily_activity = []

    current_date = start_date

    while current_date <= end_date:

        views = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='material_view'
        ).count()

        downloads = StudentActivity.objects.filter(
            activity_date__date=current_date,
            activity_type='material_download'
        ).count()

        uploads = Material.objects.filter(
            created_at__date=current_date
        ).count()

        daily_activity.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'views': views,
            'downloads': downloads,
            'uploads': uploads,
            'count': downloads
        })

        current_date += timedelta(days=1)

    # Most downloaded materials
    popular_materials = StudentActivity.objects.filter(
        activity_type='material_download',
        activity_date__date__gte=start_date
    ).values(
        'additional_info'
    ).annotate(
        download_count=Count('id')
    ).order_by(
        '-download_count'
    )[:10]

    return {
        'daily_activity': daily_activity,
        'popular_materials': list(popular_materials),
        'total_materials': Material.objects.count()
    }


# ============================================================
# STUDENT ENGAGEMENT ANALYTICS
# ============================================================

def get_student_engagement_analytics():
    """
    Get student engagement statistics.
    """

    # Feedback by program
    feedback_by_program = StuResponse.objects.filter(
        responsetype='feedback'
    ).values(
        'program'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    # Complaints by program
    complaints_by_program = StuResponse.objects.filter(
        responsetype='complain'
    ).values(
        'program'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    # Questions by program
    question_activities = StudentActivity.objects.filter(
        activity_type='question_post'
    ).values(
        'program__program'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    # Answers by program
    answer_activities = StudentActivity.objects.filter(
        activity_type='answer_post'
    ).values(
        'program__program'
    ).annotate(
        count=Count('id')
    ).order_by('-count')

    # Most active students
    most_active_students = StudentActivity.objects.values(
        'rollno',
        'student_name'
    ).annotate(
        program_name=F('program__program'),
        branch_name=F('branch__branch'),
        activity_count=Count('id')
    ).order_by(
        '-activity_count'
    )[:20]

    return {
        'feedback_by_program': list(
            feedback_by_program
        ),

        'complaints_by_program': list(
            complaints_by_program
        ),

        'questions_by_program': list(
            question_activities
        ),

        'answers_by_program': list(
            answer_activities
        ),

        'most_active_students': list(
            most_active_students
        ),

        'total_feedback': StuResponse.objects.filter(
            responsetype='feedback'
        ).count(),

        'total_complaints': StuResponse.objects.filter(
            responsetype='complain'
        ).count(),

        'total_questions': Question.objects.count(),

        'total_answers': Answer.objects.count()
    }


# ============================================================
# DASHBOARD SUMMARY
# ============================================================

def get_dashboard_summary():
    """
    Get admin dashboard summary.
    """

    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # Today's logins
    today_logins = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).count()

    # Today's unique students
    today_unique_students = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).values(
        'rollno'
    ).distinct().count()

    # Today's downloads
    today_downloads = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_download'
    ).count()

    # Today's views
    today_views = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_view'
    ).count()

    # Yesterday's logins
    yesterday_logins = StudentActivity.objects.filter(
        activity_date__date=yesterday,
        activity_type='login'
    ).count()

    # Yesterday's downloads
    yesterday_downloads = StudentActivity.objects.filter(
        activity_date__date=yesterday,
        activity_type='material_download'
    ).count()

    # Last 7 days unique students
    week_start = today - timedelta(days=7)

    week_unique_students = StudentActivity.objects.filter(
        activity_date__date__gte=week_start,
        activity_type='login'
    ).values(
        'rollno'
    ).distinct().count()

    # Login percentage change
    login_change = 0

    if yesterday_logins > 0:
        login_change = (
            (today_logins - yesterday_logins)
            / yesterday_logins
        ) * 100

    # Download percentage change
    download_change = 0

    if yesterday_downloads > 0:
        download_change = (
            (today_downloads - yesterday_downloads)
            / yesterday_downloads
        ) * 100

    return {
        'total_students': Student.objects.count(),

        'total_materials': Material.objects.count(),

        'total_courses': Course.objects.count(),

        'total_news': News.objects.count(),

        'today_logins': today_logins,

        'today_unique_students': today_unique_students,

        'week_unique_students': week_unique_students,

        'today_downloads': today_downloads,

        'today_views': today_views,

        'login_change': round(
            login_change,
            1
        ),

        'download_change': round(
            download_change,
            1
        )
    }


# ============================================================
# UPDATE DAILY STATISTICS
# ============================================================

def update_daily_stats():
    """
    Update today's daily statistics.
    """

    today = timezone.now().date()

    stats, created = DailyStats.objects.get_or_create(
        date=today
    )

    # Total students
    stats.total_students = Student.objects.count()

    # Students logged in
    stats.students_logged_in = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).values(
        'rollno'
    ).distinct().count()

    # Total logins
    stats.total_logins = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='login'
    ).count()

    # Material views
    stats.material_views = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_view'
    ).count()

    # Material downloads
    stats.material_downloads = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='material_download'
    ).count()

    # Questions
    stats.questions_posted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='question_post'
    ).count()

    # Answers
    stats.answers_posted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='answer_post'
    ).count()

    # Feedback
    stats.feedback_submitted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='feedback_submit'
    ).count()

    # Complaints
    stats.complaints_submitted = StudentActivity.objects.filter(
        activity_date__date=today,
        activity_type='complaint_submit'
    ).count()

    # Materials uploaded
    stats.materials_uploaded = Material.objects.filter(
        created_at__date=today
    ).count()

    stats.save()

    return stats


# ============================================================
# SYNC STUDENT DATA
# ============================================================

def sync_student_data():
    """
    Sync existing Student data with
    Program, Branch and Year tables.
    """

    try:

        students = Student.objects.all()

        for student in students:

            # Program
            program_obj, created = Program.objects.get_or_create(
                program=student.program
            )

            if created:
                print(
                    f"Created Program: {student.program}"
                )

            # Branch
            branch_obj, created = Branch.objects.get_or_create(
                branch=student.branch
            )

            if created:
                print(
                    f"Created Branch: {student.branch}"
                )

            # Year
            year_obj, created = Year.objects.get_or_create(
                year=student.year
            )

            if created:
                print(
                    f"Created Year: {student.year}"
                )

        print(
            f"Synced data for {students.count()} students"
        )

    except Exception as e:

        print(
            f"Error syncing student data: {e}"
        )


# ============================================================
# MIGRATE STUDENT ACTIVITY DATA
# ============================================================

def migrate_student_activity_data():
    """
    Migrate existing StudentActivity records.
    """

    try:

        activities = StudentActivity.objects.all()

        for activity in activities:

            # Program
            if isinstance(activity.program, str):

                program_obj, _ = Program.objects.get_or_create(
                    program=activity.program
                )

                activity.program = program_obj

            # Branch
            if isinstance(activity.branch, str):

                branch_obj, _ = Branch.objects.get_or_create(
                    branch=activity.branch
                )

                activity.branch = branch_obj

            # Year
            if isinstance(activity.year, str):

                year_obj, _ = Year.objects.get_or_create(
                    year=activity.year
                )

                activity.year = year_obj

            activity.save()

        print(
            f"Migrated {activities.count()} activity records"
        )

    except Exception as e:

        print(
            f"Error migrating activity data: {e}"
        )
