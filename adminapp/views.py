
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, Http404, FileResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, F
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from nouapp.models import Student, Enquiry, Login, EnquiryReply
from studentapp.models import StuResponse

from .models import (
    Program,
    Branch,
    Year,
    Material,
    News,
    Course,
    MaterialCategory,
    MaterialAccess,
    NewsAnnouncement,
    NewsCategory
)

from .forms import MaterialForm, MaterialCategoryForm

from datetime import date, datetime, timedelta

import os
import mimetypes

from PIL import Image
import pdf2image


# ============================================================
# ADMIN HOME
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminhome(request):

    try:

        adminid = request.session.get('adminid')

        if not adminid:
            return redirect('nouapp:login')

        print("ADMIN SESSION:", request.session.items())

        try:
            user = User.objects.get(
                username=adminid
            )
        except User.DoesNotExist:
            user = None

        current_hour = datetime.now().hour

        if current_hour < 12:
            greeting = "Good Morning"
            greeting_icon = "☀️"

        elif current_hour < 17:
            greeting = "Good Afternoon"
            greeting_icon = "🌤️"

        else:
            greeting = "Good Evening"
            greeting_icon = "🌙"

        if user and user.first_name:
            admin_name = user.first_name
        else:
            admin_name = adminid

        last_login = user.last_login if user else None

        total_students = Student.objects.count()

        total_materials = Material.objects.count()

        pending_enquiries = Enquiry.objects.filter(
            status='pending'
        ).count()

        recent_feedbacks = StuResponse.objects.count()

        context = {
            'adminid': adminid,
            'greeting': greeting,
            'greeting_icon': greeting_icon,
            'admin_name': admin_name,
            'last_login': last_login,
            'total_students': total_students,
            'total_materials': total_materials,
            'pending_enquiries': pending_enquiries,
            'recent_feedbacks': recent_feedbacks,
        }

        return render(
            request,
            "adminhome.html",
            context
        )

    except Exception as e:

        print(
            "ADMIN HOME ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# ADMIN LOGOUT
# ============================================================

def adminlogout(request):

    try:

        if 'adminid' in request.session:
            del request.session['adminid']

        return redirect(
            'nouapp:login'
        )

    except Exception:

        return redirect(
            'nouapp:login'
        )


# ============================================================
# VIEW STUDENTS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewstudent(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        student = Student.objects.all()

        return render(
            request,
            "viewstudent.html",
            {
                'adminid': adminid,
                'student': student
            }
        )

    except Exception as e:

        print(
            "VIEW STUDENT ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# VIEW ENQUIRY
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewenquiry(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        enq = Enquiry.objects.all()

        return render(
            request,
            "viewenquiry.html",
            {
                'adminid': adminid,
                'enq': enq
            }
        )

    except Exception as e:

        print(
            "VIEW ENQUIRY ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# VIEW FEEDBACK
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewfeedback(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        feed = StuResponse.objects.filter(
            responsetype='feedback'
        )

        return render(
            request,
            "viewfeedback.html",
            {
                'adminid': adminid,
                'feed': feed
            }
        )

    except Exception as e:

        print(
            "VIEW FEEDBACK ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# VIEW COMPLAINT
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewcomplain(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        comp = StuResponse.objects.filter(
            responsetype='complain'
        )

        return render(
            request,
            "viewcomplain.html",
            {
                'adminid': adminid,
                'comp': comp
            }
        )

    except Exception as e:

        print(
            "VIEW COMPLAINT ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# STUDY MATERIAL - ADMIN PAGE
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def studymaterial(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        courses = Course.objects.all().order_by(
            'title'
        )

        categories = MaterialCategory.objects.all().order_by(
            'name'
        )

        programs = Program.objects.all().order_by(
            'program'
        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        years = Year.objects.all().order_by(
            'year'
        )

        return render(
            request,
            "studymaterial.html",
            {
                'adminid': adminid,
                'courses': courses,
                'categories': categories,
                'programs': programs,
                'branches': branches,
                'years': years
            }
        )

    except Exception as e:

        print(
            "STUDY MATERIAL PAGE ERROR:",
            e
        )

        messages.error(
            request,
            f"Error loading study materials: {e}"
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# UPLOAD STUDY MATERIAL
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def move(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:
            return redirect(
                'nouapp:login'
            )

        if request.method != 'POST':

            return redirect(
                'adminapp:studymaterial'
            )

        course_id = request.POST.get(
            'course'
        )

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        category_id = request.POST.get(
            'category'
        )

        my_file = request.FILES.get(
            'my_file'
        )

        print("======================================")
        print("STUDY MATERIAL UPLOAD")
        print("Admin ID:", adminid)
        print("Course ID:", course_id)
        print("Title:", title)
        print("Category ID:", category_id)
        print("File:", my_file)
        print("======================================")

        if not course_id:

            messages.error(
                request,
                "Please select a course."
            )

            return redirect(
                'adminapp:studymaterial'
            )

        if not title:

            messages.error(
                request,
                "Please enter material title."
            )

            return redirect(
                'adminapp:studymaterial'
            )

        if not my_file:

            messages.error(
                request,
                "Please select a file."
            )

            return redirect(
                'adminapp:studymaterial'
            )

        course = get_object_or_404(
            Course,
            id=course_id
        )

        category = None

        if category_id:

            category = MaterialCategory.objects.filter(
                id=category_id
            ).first()

        user = None

        try:

            if str(adminid).isdigit():

                user = User.objects.filter(
                    id=int(adminid)
                ).first()

        except Exception:

            user = None

        if user is None:

            try:

                user = User.objects.filter(
                    username=str(adminid)
                ).first()

            except Exception:

                user = None

        if user is None:

            user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'first_name': 'Administrator',
                    'is_staff': True,
                    'is_superuser': True
                }
            )

        print(
            "USER USED:",
            user
        )

        print(
            "USER ID:",
            user.id
        )

        material = Material(
            title=title,
            description=description,
            course=course,
            category=category,
            file=my_file,
            created_by=user,
            is_public=True,
            requires_enrollment=False,
            version=1,
            is_latest_version=True
        )

        material.save()

        print("======================================")
        print("MATERIAL CREATED SUCCESSFULLY")
        print("Material ID:", material.id)
        print("Title:", material.title)
        print("Course:", material.course)
        print("File:", material.file.name)
        print("Public:", material.is_public)
        print("======================================")

        messages.success(
            request,
            f"Study material '{title}' uploaded successfully!"
        )

        return redirect(
            'adminapp:viewmaterial'
        )

    except Exception as e:

        print("======================================")
        print("MATERIAL UPLOAD ERROR")
        print(e)
        print("======================================")

        messages.error(
            request,
            f"Material upload failed: {e}"
        )

        return redirect(
            'adminapp:studymaterial'
        )


# ============================================================
# VIEW ALL STUDY MATERIALS - ADMIN
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def viewmaterial(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        course_filter = request.GET.get(
            'course',
            ''
        )

        category_filter = request.GET.get(
            'category',
            ''
        )

        search_query = request.GET.get(
            'search',
            ''
        )

        mat = Material.objects.select_related(
            'course',
            'course__program',
            'course__branch',
            'course__year',
            'category',
            'created_by'
        ).all()

        if course_filter:

            mat = mat.filter(
                course_id=course_filter
            )

        if category_filter:

            mat = mat.filter(
                category_id=category_filter
            )

        if search_query:

            mat = mat.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        mat = mat.order_by(
            '-created_at'
        )

        courses = Course.objects.all().order_by(
            'title'
        )

        categories = MaterialCategory.objects.all().order_by(
            'name'
        )

        print("======================================")
        print("ADMIN MATERIAL LIST")
        print("TOTAL MATERIALS:", mat.count())

        for material in mat:

            print(
                "ID:",
                material.id,
                "| TITLE:",
                material.title,
                "| FILE:",
                material.file.name
                if material.file
                else "NO FILE",
                "| PUBLIC:",
                material.is_public
            )

        print("======================================")

        return render(
            request,
            "viewmaterial.html",
            {
                'mat': mat,
                'adminid': adminid,
                'courses': courses,
                'categories': categories
            }
        )

    except Exception as e:

        print(
            "VIEW MATERIAL ERROR:",
            e
        )

        messages.error(
            request,
            f"Error loading materials: {e}"
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def news(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == "POST":

            newstext = request.POST.get(
                'newstext'
            )

            newsdate = date.today()

            News(
                newstext=newstext,
                newsdate=newsdate
            ).save()

        ns = News.objects.all()

        return render(
            request,
            "news.html",
            {
                'adminid': adminid,
                'ns': ns
            }
        )

    except Exception as e:

        print(
            "NEWS ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# ADVANCED MATERIAL MANAGEMENT
# ============================================================

@login_required
def material_list(request, course_id=None):

    materials = Material.objects.select_related(
        'category',
        'course',
        'created_by'
    )

    if course_id:

        course = get_object_or_404(
            Course,
            id=course_id
        )

        materials = materials.filter(
            course=course
        )

    category_id = request.GET.get(
        'category'
    )

    if category_id:

        materials = materials.filter(
            category_id=category_id
        )

    search_query = request.GET.get(
        'search'
    )

    if search_query:

        materials = materials.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    file_type = request.GET.get(
        'file_type'
    )

    if file_type:

        materials = materials.filter(
            file_type=file_type
        )

    show_all_versions = request.GET.get(
        'show_all_versions',
        False
    )

    if not show_all_versions:

        materials = materials.filter(
            is_latest_version=True
        )

    paginator = Paginator(
        materials,
        12
    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    categories = MaterialCategory.objects.all()

    file_types = materials.values_list(
        'file_type',
        flat=True
    ).distinct()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'file_types': file_types,
        'current_category': category_id,
        'current_file_type': file_type,
        'search_query': search_query,
        'show_all_versions': show_all_versions,
    }

    if course_id:

        context['course'] = course

    return render(
        request,
        'adminapp/material_list.html',
        context
    )


# ============================================================
# MATERIAL DETAIL
# ============================================================

@login_required
def material_detail(request, material_id):

    material = get_object_or_404(
        Material,
        id=material_id
    )

    if material.requires_enrollment:
        pass

    all_versions = material.get_all_versions()

    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='view',
        ip_address=request.META.get(
            'REMOTE_ADDR'
        ),
        user_agent=request.META.get(
            'HTTP_USER_AGENT',
            ''
        )
    )

    Material.objects.filter(
        id=material_id
    ).update(
        view_count=F(
            'view_count'
        ) + 1
    )

    context = {
        'material': material,
        'all_versions': all_versions,
        'can_edit': (
            request.user == material.created_by
            or request.user.is_staff
        ),
    }

    return render(
        request,
        'adminapp/material_detail.html',
        context
    )


# ============================================================
# MATERIAL PREVIEW
# ============================================================

@login_required
def material_preview(request, material_id):

    material = get_object_or_404(
        Material,
        id=material_id
    )

    if not material.is_previewable:

        return JsonResponse(
            {
                'error':
                    'Preview not available for this file type'
            },
            status=400
        )

    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='preview',
        ip_address=request.META.get(
            'REMOTE_ADDR'
        ),
        user_agent=request.META.get(
            'HTTP_USER_AGENT',
            ''
        )
    )

    try:

        if material.file_type in [
            'jpg',
            'jpeg',
            'png',
            'gif'
        ]:

            return FileResponse(
                material.file.open(),
                content_type=f'image/{material.file_type}'
            )

        elif material.file_type == 'pdf':

            if material.preview_image:

                return FileResponse(
                    material.preview_image.open(),
                    content_type='image/png'
                )

            else:

                preview_path = generate_pdf_preview(
                    material
                )

                if preview_path:

                    return FileResponse(
                        open(
                            preview_path,
                            'rb'
                        ),
                        content_type='image/png'
                    )

        elif material.file_type == 'txt':

            with material.file.open(
                'r'
            ) as f:

                content = f.read(
                    500
                )

                return JsonResponse(
                    {
                        'preview_text': content,
                        'type': 'text'
                    }
                )

        elif material.file_type == 'mp4':

            return JsonResponse(
                {
                    'video_url':
                        material.file.url,
                    'type':
                        'video'
                }
            )

    except Exception as e:

        return JsonResponse(
            {
                'error':
                    f'Error generating preview: {str(e)}'
            },
            status=500
        )

    return JsonResponse(
        {
            'error':
                'Preview generation failed'
        },
        status=500
    )


# ============================================================
# PDF PREVIEW
# ============================================================

def generate_pdf_preview(material):

    try:

        images = pdf2image.convert_from_path(
            material.file.path,
            first_page=1,
            last_page=1
        )

        if images:

            preview_path = (
                f"media/previews/"
                f"{material.id}_preview.png"
            )

            os.makedirs(
                os.path.dirname(
                    preview_path
                ),
                exist_ok=True
            )

            images[0].save(
                preview_path,
                'PNG'
            )

            material.preview_image = preview_path

            material.save()

            return preview_path

    except Exception as e:

        print(
            f"Error generating PDF preview: {e}"
        )

    return None


# ============================================================
# MATERIAL DOWNLOAD
# ============================================================

@login_required
def material_download(request, material_id):

    material = get_object_or_404(
        Material,
        id=material_id
    )

    if material.requires_enrollment:
        pass

    MaterialAccess.objects.create(
        material=material,
        user=request.user,
        access_type='download',
        ip_address=request.META.get(
            'REMOTE_ADDR'
        ),
        user_agent=request.META.get(
            'HTTP_USER_AGENT',
            ''
        )
    )

    Material.objects.filter(
        id=material_id
    ).update(
        download_count=F(
            'download_count'
        ) + 1
    )

    response = FileResponse(
        material.file.open(),
        content_type=mimetypes.guess_type(
            material.file.path
        )[0],
        as_attachment=True,
        filename=material.file.name.split(
            '/'
        )[-1]
    )

    return response


# ============================================================
# CREATE MATERIAL
# ============================================================

@login_required
def create_material(request, course_id):

    course = get_object_or_404(
        Course,
        id=course_id
    )

    if not (
        request.user.is_staff
        or course.instructor == request.user
    ):

        messages.error(
            request,
            "You don't have permission to add materials to this course."
        )

        return redirect(
            'adminapp:material_list',
            course_id=course_id
        )

    if request.method == 'POST':

        form = MaterialForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            material = form.save(
                commit=False
            )

            material.course = course

            material.created_by = request.user

            material.save()

            messages.success(
                request,
                'Material uploaded successfully!'
            )

            return redirect(
                'adminapp:material_detail',
                material_id=material.id
            )

    else:

        form = MaterialForm()

    return render(
        request,
        'adminapp/create_material.html',
        {
            'form': form,
            'course': course
        }
    )


# ============================================================
# CREATE MATERIAL VERSION
# ============================================================

@login_required
def create_material_version(
    request,
    material_id
):

    original_material = get_object_or_404(
        Material,
        id=material_id
    )

    if not (
        request.user.is_staff
        or original_material.created_by == request.user
    ):

        messages.error(
            request,
            "You don't have permission to create versions of this material."
        )

        return redirect(
            'adminapp:material_detail',
            material_id=material_id
        )

    if request.method == 'POST':

        form = MaterialForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            new_version = form.save(
                commit=False
            )

            new_version.course = (
                original_material.course
            )

            new_version.created_by = (
                request.user
            )

            new_version.parent_material = (
                original_material
                if not original_material.parent_material
                else original_material.parent_material
            )

            new_version.save()

            messages.success(
                request,
                f'New version ({new_version.version}) created successfully!'
            )

            return redirect(
                'adminapp:material_detail',
                material_id=new_version.id
            )

    else:

        form = MaterialForm(
            initial={
                'title':
                    original_material.title,
                'description':
                    original_material.description,
                'category':
                    original_material.category,
                'is_public':
                    original_material.is_public,
                'requires_enrollment':
                    original_material.requires_enrollment,
            }
        )

    return render(
        request,
        'adminapp/create_material_version.html',
        {
            'form': form,
            'original_material':
                original_material
        }
    )


# ============================================================
# MATERIAL CATEGORIES
# ============================================================

@login_required
def material_categories(request):

    categories = MaterialCategory.objects.all()

    if request.method == 'POST':

        form = MaterialCategoryForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Category created successfully!'
            )

            return redirect(
                'adminapp:material_categories'
            )

    else:

        form = MaterialCategoryForm()

    return render(
        request,
        'adminapp/material_categories.html',
        {
            'categories': categories,
            'form': form
        }
    )


# ============================================================
# DELETE MATERIAL
# ============================================================

@require_http_methods(["POST"])
@login_required
def delete_material(request, material_id):

    material = get_object_or_404(
        Material,
        id=material_id
    )

    if not (
        request.user.is_staff
        or material.created_by == request.user
    ):

        return JsonResponse(
            {
                'error':
                    'Permission denied'
            },
            status=403
        )

    course_id = (
        material.course.id
        if material.course
        else None
    )

    material.delete()

    messages.success(
        request,
        'Material deleted successfully!'
    )

    if course_id:

        return redirect(
            'adminapp:course_materials',
            course_id=course_id
        )

    return redirect(
        'adminapp:material_list'
    )


# ============================================================
# MANAGE NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_news(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        category_filter = request.GET.get(
            'category',
            ''
        )

        status_filter = request.GET.get(
            'status',
            'all'
        )

        news_list = NewsAnnouncement.objects.all().select_related(
            'category'
        )

        if category_filter:

            news_list = news_list.filter(
                category_id=category_filter
            )

        if status_filter == 'active':

            now = timezone.now()

            news_list = news_list.filter(
                is_active=True,
                publish_date__lte=now
            ).exclude(
                expiry_date__lt=now
            )

        elif status_filter == 'expired':

            news_list = news_list.filter(
                expiry_date__lt=timezone.now()
            )

        categories = NewsCategory.objects.filter(
            is_active=True
        )

        return render(
            request,
            "manage_news.html",
            {
                'adminid': adminid,
                'news_list': news_list,
                'categories': categories,
                'current_category': category_filter,
                'current_status': status_filter
            }
        )

    except Exception as e:

        print(
            "MANAGE NEWS ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# CREATE NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_news(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            title = request.POST.get(
                'title'
            )

            newstext = request.POST.get(
                'newstext'
            )

            category_id = request.POST.get(
                'category'
            )

            priority = request.POST.get(
                'priority',
                'normal'
            )

            target_audience = request.POST.get(
                'target_audience',
                'all'
            )

            publish_date_str = request.POST.get(
                'publish_date'
            )

            expiry_date_str = request.POST.get(
                'expiry_date'
            )

            target_programs = request.POST.getlist(
                'target_programs'
            )

            target_branches = request.POST.getlist(
                'target_branches'
            )

            target_years = request.POST.getlist(
                'target_years'
            )

            if not title or not newstext:

                messages.error(
                    request,
                    "Title and content are required!"
                )

                return render(
                    request,
                    "create_news.html",
                    {
                        'adminid': adminid,
                        'categories':
                            NewsCategory.objects.filter(
                                is_active=True
                            ),
                        'programs':
                            Program.objects.all(),
                        'branches':
                            Branch.objects.all(),
                        'years':
                            Year.objects.all()
                    }
                )

            publish_date = timezone.now()

            if publish_date_str:

                try:

                    naive_dt = datetime.strptime(
                        publish_date_str,
                        '%Y-%m-%dT%H:%M'
                    )

                    publish_date = timezone.make_aware(
                        naive_dt
                    )

                except ValueError:

                    messages.error(
                        request,
                        "Invalid publish date format!"
                    )

                    return redirect(
                        'adminapp:create_news'
                    )

            expiry_date = None

            if expiry_date_str:

                try:

                    naive_dt = datetime.strptime(
                        expiry_date_str,
                        '%Y-%m-%dT%H:%M'
                    )

                    expiry_date = timezone.make_aware(
                        naive_dt
                    )

                except ValueError:

                    messages.error(
                        request,
                        "Invalid expiry date format!"
                    )

                    return redirect(
                        'adminapp:create_news'
                    )

            news = NewsAnnouncement.objects.create(
                title=title,
                newstext=newstext,
                category_id=(
                    category_id
                    if category_id
                    else None
                ),
                priority=priority,
                target_audience=target_audience,
                publish_date=publish_date,
                expiry_date=expiry_date,
                created_by=f"Admin_{adminid}",
                is_pinned=bool(
                    request.POST.get(
                        'is_pinned'
                    )
                ),
                attachment=request.FILES.get(
                    'attachment'
                ),
                is_active=True
            )

            if target_programs:

                news.target_programs.set(
                    target_programs
                )

            if target_branches:

                news.target_branches.set(
                    target_branches
                )

            if target_years:

                news.target_years.set(
                    target_years
                )

            messages.success(
                request,
                "News/Announcement created successfully!"
            )

            return redirect(
                'adminapp:manage_news'
            )

        categories = NewsCategory.objects.filter(
            is_active=True
        )

        programs = Program.objects.all()

        branches = Branch.objects.all()

        years = Year.objects.all()

        return render(
            request,
            "create_news.html",
            {
                'adminid': adminid,
                'categories': categories,
                'programs': programs,
                'branches': branches,
                'years': years
            }
        )

    except Exception as e:

        print(
            "CREATE NEWS ERROR:",
            e
        )

        messages.error(
            request,
            f"Error: {e}"
        )

        return redirect(
            'adminapp:manage_news'
        )


# ============================================================
# EDIT NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_news(request, news_id):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        if request.method == 'POST':

            news.title = request.POST.get(
                'title'
            )

            news.newstext = request.POST.get(
                'newstext'
            )

            news.category_id = (
                request.POST.get(
                    'category'
                )
                or None
            )

            news.priority = request.POST.get(
                'priority',
                'normal'
            )

            news.target_audience = request.POST.get(
                'target_audience',
                'all'
            )

            news.is_pinned = bool(
                request.POST.get(
                    'is_pinned'
                )
            )

            target_programs = request.POST.getlist(
                'target_programs'
            )

            target_branches = request.POST.getlist(
                'target_branches'
            )

            target_years = request.POST.getlist(
                'target_years'
            )

            publish_date = request.POST.get(
                'publish_date'
            )

            if publish_date:

                naive_dt = datetime.strptime(
                    publish_date,
                    '%Y-%m-%dT%H:%M'
                )

                news.publish_date = timezone.make_aware(
                    naive_dt
                )

            expiry_date = request.POST.get(
                'expiry_date'
            )

            if expiry_date:

                naive_dt = datetime.strptime(
                    expiry_date,
                    '%Y-%m-%dT%H:%M'
                )

                news.expiry_date = timezone.make_aware(
                    naive_dt
                )

            else:

                news.expiry_date = None

            if request.FILES.get(
                'attachment'
            ):

                news.attachment = request.FILES.get(
                    'attachment'
                )

            news.save()

            news.target_programs.set(
                target_programs
            )

            news.target_branches.set(
                target_branches
            )

            news.target_years.set(
                target_years
            )

            messages.success(
                request,
                "News/Announcement updated successfully!"
            )

            return redirect(
                'adminapp:manage_news'
            )

        categories = NewsCategory.objects.filter(
            is_active=True
        )

        programs = Program.objects.all()

        branches = Branch.objects.all()

        years = Year.objects.all()

        return render(
            request,
            "edit_news.html",
            {
                'adminid': adminid,
                'news': news,
                'categories': categories,
                'programs': programs,
                'branches': branches,
                'years': years
            }
        )

    except Exception as e:

        print(
            "EDIT NEWS ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_news'
        )


# ============================================================
# MANAGE NEWS CATEGORIES
# ============================================================

def manage_categories(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            if 'edit_category' in request.POST:

                category_id = request.POST.get(
                    'edit_category'
                )

                category = get_object_or_404(
                    NewsCategory,
                    id=category_id
                )

                category.name = request.POST.get(
                    'edit_name'
                )

                category.description = request.POST.get(
                    'edit_description',
                    ''
                )

                category.icon = request.POST.get(
                    'edit_icon',
                    ''
                )

                category.color_code = request.POST.get(
                    'edit_color_code',
                    '#007bff'
                )

                category.is_active = bool(
                    request.POST.get(
                        'edit_is_active'
                    )
                )

                category.save()

                messages.success(
                    request,
                    "Category updated successfully!"
                )

            else:

                name = request.POST.get(
                    'name'
                )

                description = request.POST.get(
                    'description',
                    ''
                )

                icon = request.POST.get(
                    'icon',
                    ''
                )

                color_code = request.POST.get(
                    'color_code',
                    '#007bff'
                )

                if name:

                    NewsCategory.objects.create(
                        name=name,
                        description=description,
                        icon=icon,
                        color_code=color_code
                    )

                    messages.success(
                        request,
                        "Category created successfully!"
                    )

                else:

                    messages.error(
                        request,
                        "Category name is required!"
                    )

        categories = NewsCategory.objects.all().order_by(
            'name'
        )

        return render(
            request,
            "manage_categories.html",
            {
                'adminid': adminid,
                'categories': categories
            }
        )

    except Exception as e:

        print(
            "CATEGORY ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# NEWS STATUS
# ============================================================

def toggle_news_status(request, news_id):

    try:

        if not request.session.get(
            'adminid'
        ):

            return redirect(
                'nouapp:login'
            )

        news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        news.is_active = not news.is_active

        news.save()

        status = (
            "activated"
            if news.is_active
            else "deactivated"
        )

        messages.success(
            request,
            f"News {status} successfully!"
        )

    except Exception as e:

        print(
            "TOGGLE NEWS ERROR:",
            e
        )

    return redirect(
        'adminapp:manage_news'
    )


# ============================================================
# DELETE NEWS
# ============================================================

def delete_news(request, news_id):

    try:

        if not request.session.get(
            'adminid'
        ):

            return redirect(
                'nouapp:login'
            )

        news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        news.delete()

        messages.success(
            request,
            "News deleted successfully!"
        )

    except Exception as e:

        print(
            "DELETE NEWS ERROR:",
            e
        )

    return redirect(
        'adminapp:manage_news'
    )


# ============================================================
# PIN NEWS
# ============================================================

def pin_news(request, news_id):

    try:

        if not request.session.get(
            'adminid'
        ):

            return redirect(
                'nouapp:login'
            )

        news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        news.is_pinned = not news.is_pinned

        news.save()

        status = (
            "pinned"
            if news.is_pinned
            else "unpinned"
        )

        messages.success(
            request,
            f"News {status} successfully!"
        )

    except Exception as e:

        print(
            "PIN NEWS ERROR:",
            e
        )

    return redirect(
        'adminapp:manage_news'
    )


# ============================================================
# NEWS STATISTICS
# ============================================================

def get_news_stats():

    today = timezone.now().date()

    week_ago = (
        today - timedelta(days=7)
    )

    total_news = NewsAnnouncement.objects.count()

    active_news = NewsAnnouncement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).exclude(
        expiry_date__lt=timezone.now()
    ).count()

    news_this_week = NewsAnnouncement.objects.filter(
        newsdate__date__gte=week_ago
    ).count()

    expired_news = NewsAnnouncement.objects.filter(
        expiry_date__lt=timezone.now()
    ).count()

    return {
        'total_news': total_news,
        'active_news': active_news,
        'news_this_week': news_this_week,
        'expired_news': expired_news
    }


# ============================================================
# CLEANUP EXPIRED NEWS
# ============================================================

def cleanup_expired_news():

    expired_count = NewsAnnouncement.objects.filter(
        expiry_date__lt=timezone.now(),
        is_active=True
    ).update(
        is_active=False
    )

    return expired_count


# ============================================================
# ENHANCED ADMIN DASHBOARD
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def enhanced_admin_dashboard(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        news_stats = get_news_stats()

        recent_news = NewsAnnouncement.objects.filter(
            is_active=True
        ).order_by(
            '-publish_date'
        )[:5]

        urgent_news = NewsAnnouncement.objects.filter(
            is_active=True,
            priority='urgent',
            publish_date__lte=timezone.now()
        ).exclude(
            expiry_date__lt=timezone.now()
        )

        return render(
            request,
            "enhanced_admin_dashboard.html",
            {
                'adminid': adminid,
                'news_stats': news_stats,
                'recent_news': recent_news,
                'urgent_news': urgent_news
            }
        )

    except Exception as e:

        print(
            "ENHANCED DASHBOARD ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# BULK NEWS ACTION
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def bulk_news_action(request):

    try:

        if not request.session.get(
            'adminid'
        ):

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            action = request.POST.get(
                'bulk_action'
            )

            selected_news = request.POST.getlist(
                'selected_news'
            )

            if not selected_news:

                messages.error(
                    request,
                    "No news items selected!"
                )

                return redirect(
                    'adminapp:manage_news'
                )

            if not action:

                messages.error(
                    request,
                    "No action selected!"
                )

                return redirect(
                    'adminapp:manage_news'
                )

            news_items = NewsAnnouncement.objects.filter(
                nid__in=selected_news
            )

            count = news_items.count()

            if action == 'activate':

                news_items.update(
                    is_active=True
                )

                messages.success(
                    request,
                    f"Activated {count} news items successfully!"
                )

            elif action == 'deactivate':

                news_items.update(
                    is_active=False
                )

                messages.success(
                    request,
                    f"Deactivated {count} news items successfully!"
                )

            elif action == 'delete':

                news_items.delete()

                messages.success(
                    request,
                    f"Deleted {count} news items successfully!"
                )

            elif action == 'pin':

                news_items.update(
                    is_pinned=True
                )

                messages.success(
                    request,
                    f"Pinned {count} news items successfully!"
                )

            elif action == 'unpin':

                news_items.update(
                    is_pinned=False
                )

                messages.success(
                    request,
                    f"Unpinned {count} news items successfully!"
                )

            else:

                messages.error(
                    request,
                    "Invalid action selected!"
                )

        return redirect(
            'adminapp:manage_news'
        )

    except Exception as e:

        print(
            "BULK NEWS ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_news'
        )


# ============================================================
# DUPLICATE NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def duplicate_news(request, news_id):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        original_news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        duplicate = NewsAnnouncement.objects.create(
            title=f"Copy of {original_news.title}",
            newstext=original_news.newstext,
            category=original_news.category,
            priority=original_news.priority,
            target_audience=original_news.target_audience,
            publish_date=timezone.now(),
            expiry_date=original_news.expiry_date,
            created_by=f"Admin_{adminid}",
            is_active=False,
            is_pinned=False,
        )

        duplicate.target_programs.set(
            original_news.target_programs.all()
        )

        duplicate.target_branches.set(
            original_news.target_branches.all()
        )

        duplicate.target_years.set(
            original_news.target_years.all()
        )

        messages.success(
            request,
            "News item duplicated successfully! Please review and activate."
        )

        return redirect(
            'adminapp:edit_news',
            news_id=duplicate.nid
        )

    except Exception as e:

        print(
            "DUPLICATE NEWS ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_news'
        )


# ============================================================
# PREVIEW NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def preview_news(request, news_id):

    try:

        if not request.session.get(
            'adminid'
        ):

            return redirect(
                'nouapp:login'
            )

        news = get_object_or_404(
            NewsAnnouncement,
            nid=news_id
        )

        programs_list = list(
            news.target_programs.values_list(
                'program',
                flat=True
            )
        )

        branches_list = list(
            news.target_branches.values_list(
                'branch',
                flat=True
            )
        )

        years_list = list(
            news.target_years.values_list(
                'year',
                flat=True
            )
        )

        preview_html = f"""
        <div class="news-preview">

            <div class="mb-3">

                <h4>{news.title}</h4>

                <div class="mb-2">

                    <span class="badge badge-primary">
                        {news.get_priority_display()}
                    </span>

                    {
                        f'<span class="badge ml-1" style="background-color: {news.category.color_code};">{news.category.name}</span>'
                        if news.category
                        else ''
                    }

                    {
                        '<span class="badge badge-warning ml-1">Pinned</span>'
                        if news.is_pinned
                        else ''
                    }

                </div>

            </div>

            <div class="mb-3">

                <strong>Target Audience:</strong>
                {news.get_target_audience_display()}

                {
                    f'<br><strong>Programs:</strong> {", ".join(programs_list)}'
                    if programs_list
                    else ''
                }

                {
                    f'<br><strong>Branches:</strong> {", ".join(branches_list)}'
                    if branches_list
                    else ''
                }

                {
                    f'<br><strong>Years:</strong> {", ".join(years_list)}'
                    if years_list
                    else ''
                }

            </div>

            <div class="mb-3">

                <strong>Content:</strong>

                <div class="mt-2 p-3 bg-light border-left border-primary">

                    {news.newstext.replace(chr(10), '<br>')}

                </div>

            </div>

            <div class="row">

                <div class="col-md-6">

                    <strong>Publish Date:</strong><br>

                    {
                        news.publish_date.strftime(
                            '%B %d, %Y at %I:%M %p'
                        )
                    }

                </div>

                <div class="col-md-6">

                    <strong>Expiry Date:</strong><br>

                    {
                        news.expiry_date.strftime(
                            '%B %d, %Y at %I:%M %p'
                        )
                        if news.expiry_date
                        else 'Never expires'
                    }

                </div>

            </div>

            {
                f'<div class="mt-3"><strong>Attachment:</strong> <a href="{news.attachment.url}" target="_blank">{news.attachment.name}</a></div>'
                if news.attachment
                else ''
            }

            <div class="mt-3 text-muted">

                <small>
                    Created by: {news.created_by}
                    | Views: {news.view_count}
                </small>

            </div>

        </div>
        """

        return HttpResponse(
            preview_html
        )

    except Exception as e:

        print(
            "PREVIEW NEWS ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_news'
        )


# ============================================================
# NEWS ANALYTICS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def news_analytics(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        total_news = NewsAnnouncement.objects.count()

        active_news = NewsAnnouncement.objects.filter(
            is_active=True
        ).count()

        category_stats = NewsCategory.objects.annotate(
            news_count=Count(
                'newsannouncement'
            )
        ).order_by(
            '-news_count'
        )

        priority_stats = NewsAnnouncement.objects.values(
            'priority'
        ).annotate(
            count=Count('priority')
        ).order_by(
            'priority'
        )

        thirty_days_ago = (
            timezone.now()
            - timedelta(days=30)
        )

        recent_news = NewsAnnouncement.objects.filter(
            newsdate__gte=thirty_days_ago
        ).count()

        popular_news = NewsAnnouncement.objects.filter(
            is_active=True
        ).order_by(
            '-view_count'
        )[:10]

        seven_days_later = (
            timezone.now()
            + timedelta(days=7)
        )

        expiring_soon = NewsAnnouncement.objects.filter(
            expiry_date__lte=seven_days_later,
            expiry_date__gt=timezone.now(),
            is_active=True
        ).count()

        context = {
            'adminid': adminid,
            'total_news': total_news,
            'active_news': active_news,
            'recent_news': recent_news,
            'expiring_soon': expiring_soon,
            'category_stats': category_stats,
            'priority_stats': priority_stats,
            'popular_news': popular_news,
        }

        return render(
            request,
            "news_analytics.html",
            context
        )

    except Exception as e:

        print(
            "NEWS ANALYTICS ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# ENHANCED MANAGE NEWS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_news_enhanced(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        category_filter = request.GET.get(
            'category',
            ''
        )

        status_filter = request.GET.get(
            'status',
            'all'
        )

        priority_filter = request.GET.get(
            'priority',
            ''
        )

        search_query = request.GET.get(
            'search',
            ''
        )

        news_list = NewsAnnouncement.objects.all().select_related(
            'category'
        )

        all_news = NewsAnnouncement.objects.all().select_related(
            'category'
        )

        now = timezone.now()

        active_count = all_news.filter(
            is_active=True,
            publish_date__lte=now
        ).exclude(
            expiry_date__lt=now
        ).count()

        scheduled_count = all_news.filter(
            is_active=True,
            publish_date__gt=now
        ).count()

        expired_count = all_news.filter(
            expiry_date__lt=now
        ).count()

        inactive_count = all_news.filter(
            is_active=False
        ).count()

        total_count = all_news.count()

        if search_query:

            news_list = news_list.filter(
                Q(title__icontains=search_query) |
                Q(newstext__icontains=search_query)
            )

        if category_filter:

            news_list = news_list.filter(
                category_id=category_filter
            )

        if priority_filter:

            news_list = news_list.filter(
                priority=priority_filter
            )

        if status_filter == 'active':

            news_list = news_list.filter(
                is_active=True,
                publish_date__lte=now
            ).exclude(
                expiry_date__lt=now
            )

        elif status_filter == 'expired':

            news_list = news_list.filter(
                expiry_date__lt=now
            )

        elif status_filter == 'scheduled':

            news_list = news_list.filter(
                is_active=True,
                publish_date__gt=now
            )

        elif status_filter == 'inactive':

            news_list = news_list.filter(
                is_active=False
            )

        news_list = news_list.order_by(
            '-newsdate'
        )

        paginator = Paginator(
            news_list,
            20
        )

        page = request.GET.get(
            'page'
        )

        try:

            news_list = paginator.page(
                page
            )

        except PageNotAnInteger:

            news_list = paginator.page(
                1
            )

        except EmptyPage:

            news_list = paginator.page(
                paginator.num_pages
            )

        categories = NewsCategory.objects.filter(
            is_active=True
        )

        news_stats = {
            'total_count':
                total_count,
            'active_count':
                active_count,
            'scheduled_count':
                scheduled_count,
            'expired_count':
                expired_count,
            'inactive_count':
                inactive_count
        }

        return render(
            request,
            "manage_news.html",
            {
                'adminid': adminid,
                'news_list': news_list,
                'categories': categories,
                'current_category': category_filter,
                'current_status': status_filter,
                'current_priority': priority_filter,
                'search_query': search_query,
                'is_paginated':
                    news_list.has_other_pages(),
                'page_obj': news_list,
                'news_stats': news_stats,
            }
        )

    except Exception as e:

        print(
            "MANAGE NEWS ENHANCED ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# INCREMENT NEWS VIEW
# ============================================================

def increment_news_view(request, news_id):

    if request.method == 'POST':

        try:

            news = NewsAnnouncement.objects.get(
                nid=news_id
            )

            news.view_count += 1

            news.save()

            return JsonResponse(
                {
                    'status':
                        'success',
                    'view_count':
                        news.view_count
                }
            )

        except NewsAnnouncement.DoesNotExist:

            return JsonResponse(
                {
                    'status':
                        'error',
                    'message':
                        'News not found'
                }
            )

    return JsonResponse(
        {
            'status':
                'error',
            'message':
                'Invalid request'
        }
    )


# ============================================================
# MANAGE ACADEMIC DATA
# ============================================================

def manage_academic_data(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        programs = Program.objects.all().order_by(
            'program'
        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        years = Year.objects.all().order_by(
            'year'
        )

        courses = Course.objects.all()

        return render(
            request,
            "manage_academic_data.html",
            {
                'adminid': adminid,
                'programs': programs,
                'branches': branches,
                'years': years,
                'courses': courses
            }
        )

    except Exception as e:

        print(
            "ACADEMIC DATA ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# MANAGE PROGRAMS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_programs(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            action = request.POST.get(
                'action'
            )

            if action == 'add':

                program_name = request.POST.get(
                    'program_name',
                    ''
                ).strip()

                if program_name:

                    if not Program.objects.filter(
                        program=program_name
                    ).exists():

                        Program.objects.create(
                            program=program_name
                        )

                        messages.success(
                            request,
                            f"Program '{program_name}' added successfully!"
                        )

                    else:

                        messages.error(
                            request,
                            f"Program '{program_name}' already exists!"
                        )

                else:

                    messages.error(
                        request,
                        "Program name cannot be empty!"
                    )

            elif action == 'edit':

                program_id = request.POST.get(
                    'program_id'
                )

                new_name = request.POST.get(
                    'new_program_name',
                    ''
                ).strip()

                if program_id and new_name:

                    try:

                        program = Program.objects.get(
                            id=program_id
                        )

                        if not Program.objects.filter(
                            program=new_name
                        ).exclude(
                            id=program_id
                        ).exists():

                            program.program = new_name

                            program.save()

                            messages.success(
                                request,
                                f"Program updated to '{new_name}' successfully!"
                            )

                        else:

                            messages.error(
                                request,
                                f"Program '{new_name}' already exists!"
                            )

                    except Program.DoesNotExist:

                        messages.error(
                            request,
                            "Program not found!"
                        )

            elif action == 'delete':

                program_id = request.POST.get(
                    'program_id'
                )

                if program_id:

                    try:

                        program = Program.objects.get(
                            id=program_id
                        )

                        course_count = Course.objects.filter(
                            program=program
                        ).count()

                        if course_count > 0:

                            messages.error(
                                request,
                                f"Cannot delete program '{program.program}'. It is used in {course_count} courses."
                            )

                        else:

                            program_name = program.program

                            program.delete()

                            messages.success(
                                request,
                                f"Program '{program_name}' deleted successfully!"
                            )

                    except Program.DoesNotExist:

                        messages.error(
                            request,
                            "Program not found!"
                        )

        programs = Program.objects.all().order_by(
            'program'
        )

        return render(
            request,
            "manage_programs.html",
            {
                'adminid': adminid,
                'programs': programs
            }
        )

    except Exception as e:

        print(
            "PROGRAM ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# MANAGE BRANCHES
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_branches(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            action = request.POST.get(
                'action'
            )

            if action == 'add':

                branch_name = request.POST.get(
                    'branch_name',
                    ''
                ).strip()

                if branch_name:

                    if not Branch.objects.filter(
                        branch=branch_name
                    ).exists():

                        Branch.objects.create(
                            branch=branch_name
                        )

                        messages.success(
                            request,
                            f"Branch '{branch_name}' added successfully!"
                        )

                    else:

                        messages.error(
                            request,
                            f"Branch '{branch_name}' already exists!"
                        )

                else:

                    messages.error(
                        request,
                        "Branch name cannot be empty!"
                    )

            elif action == 'edit':

                branch_id = request.POST.get(
                    'branch_id'
                )

                new_name = request.POST.get(
                    'new_branch_name',
                    ''
                ).strip()

                if branch_id and new_name:

                    try:

                        branch = Branch.objects.get(
                            id=branch_id
                        )

                        if not Branch.objects.filter(
                            branch=new_name
                        ).exclude(
                            id=branch_id
                        ).exists():

                            branch.branch = new_name

                            branch.save()

                            messages.success(
                                request,
                                f"Branch updated to '{new_name}' successfully!"
                            )

                        else:

                            messages.error(
                                request,
                                f"Branch '{new_name}' already exists!"
                            )

                    except Branch.DoesNotExist:

                        messages.error(
                            request,
                            "Branch not found!"
                        )

            elif action == 'delete':

                branch_id = request.POST.get(
                    'branch_id'
                )

                if branch_id:

                    try:

                        branch = Branch.objects.get(
                            id=branch_id
                        )

                        course_count = Course.objects.filter(
                            branch=branch
                        ).count()

                        if course_count > 0:

                            messages.error(
                                request,
                                f"Cannot delete branch '{branch.branch}'. It is used in {course_count} courses."
                            )

                        else:

                            branch_name = branch.branch

                            branch.delete()

                            messages.success(
                                request,
                                f"Branch '{branch_name}' deleted successfully!"
                            )

                    except Branch.DoesNotExist:

                        messages.error(
                            request,
                            "Branch not found!"
                        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        return render(
            request,
            "manage_branches.html",
            {
                'adminid': adminid,
                'branches': branches
            }
        )

    except Exception as e:

        print(
            "BRANCH ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# MANAGE YEARS
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_years(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            action = request.POST.get(
                'action'
            )

            if action == 'add':

                year_name = request.POST.get(
                    'year_name',
                    ''
                ).strip()

                if year_name:

                    if not Year.objects.filter(
                        year=year_name
                    ).exists():

                        Year.objects.create(
                            year=year_name
                        )

                        messages.success(
                            request,
                            f"Year '{year_name}' added successfully!"
                        )

                    else:

                        messages.error(
                            request,
                            f"Year '{year_name}' already exists!"
                        )

                else:

                    messages.error(
                        request,
                        "Year name cannot be empty!"
                    )

            elif action == 'edit':

                year_id = request.POST.get(
                    'year_id'
                )

                new_name = request.POST.get(
                    'new_year_name',
                    ''
                ).strip()

                if year_id and new_name:

                    try:

                        year = Year.objects.get(
                            id=year_id
                        )

                        if not Year.objects.filter(
                            year=new_name
                        ).exclude(
                            id=year_id
                        ).exists():

                            year.year = new_name

                            year.save()

                            messages.success(
                                request,
                                f"Year updated to '{new_name}' successfully!"
                            )

                        else:

                            messages.error(
                                request,
                                f"Year '{new_name}' already exists!"
                            )

                    except Year.DoesNotExist:

                        messages.error(
                            request,
                            "Year not found!"
                        )

            elif action == 'delete':

                year_id = request.POST.get(
                    'year_id'
                )

                if year_id:

                    try:

                        year = Year.objects.get(
                            id=year_id
                        )

                        course_count = Course.objects.filter(
                            year=year
                        ).count()

                        if course_count > 0:

                            messages.error(
                                request,
                                f"Cannot delete year '{year.year}'. It is used in {course_count} courses."
                            )

                        else:

                            year_name = year.year

                            year.delete()

                            messages.success(
                                request,
                                f"Year '{year_name}' deleted successfully!"
                            )

                    except Year.DoesNotExist:

                        messages.error(
                            request,
                            "Year not found!"
                        )

        years = Year.objects.all().order_by(
            'year'
        )

        return render(
            request,
            "manage_years.html",
            {
                'adminid': adminid,
                'years': years
            }
        )

    except Exception as e:

        print(
            "YEAR ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# MANAGE COURSES
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def manage_courses(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        program_filter = request.GET.get(
            'program',
            ''
        )

        branch_filter = request.GET.get(
            'branch',
            ''
        )

        year_filter = request.GET.get(
            'year',
            ''
        )

        search_query = request.GET.get(
            'search',
            ''
        )

        courses = Course.objects.select_related(
            'program',
            'branch',
            'year'
        ).all()

        if program_filter:

            courses = courses.filter(
                program_id=program_filter
            )

        if branch_filter:

            courses = courses.filter(
                branch_id=branch_filter
            )

        if year_filter:

            courses = courses.filter(
                year_id=year_filter
            )

        if search_query:

            courses = courses.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        courses = courses.order_by(
            'title'
        )

        programs = Program.objects.all().order_by(
            'program'
        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        years = Year.objects.all().order_by(
            'year'
        )

        return render(
            request,
            "manage_courses.html",
            {
                'adminid': adminid,
                'courses': courses,
                'programs': programs,
                'branches': branches,
                'years': years,
                'current_program': program_filter,
                'current_branch': branch_filter,
                'current_year': year_filter,
                'search_query': search_query
            }
        )

    except Exception as e:

        print(
            "MANAGE COURSES ERROR:",
            e
        )

        return redirect(
            'nouapp:login'
        )


# ============================================================
# CREATE COURSE
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def create_course(request):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        if request.method == 'POST':

            title = request.POST.get(
                'title',
                ''
            ).strip()

            description = request.POST.get(
                'description',
                ''
            ).strip()

            program_id = request.POST.get(
                'program'
            )

            branch_id = request.POST.get(
                'branch'
            )

            year_id = request.POST.get(
                'year'
            )

            if not title or not program_id or not branch_id or not year_id:

                messages.error(
                    request,
                    "Course title, program, branch, and year are required!"
                )

                return redirect(
                    'adminapp:create_course'
                )

            if Course.objects.filter(
                title=title,
                program_id=program_id,
                branch_id=branch_id,
                year_id=year_id
            ).exists():

                messages.error(
                    request,
                    "A course with this title already exists for this program/branch/year combination!"
                )

                return redirect(
                    'adminapp:create_course'
                )

            Course.objects.create(
                title=title,
                description=description,
                program_id=program_id,
                branch_id=branch_id,
                year_id=year_id
            )

            messages.success(
                request,
                f"Course '{title}' created successfully!"
            )

            return redirect(
                'adminapp:manage_courses'
            )

        programs = Program.objects.all().order_by(
            'program'
        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        years = Year.objects.all().order_by(
            'year'
        )

        return render(
            request,
            "create_course.html",
            {
                'adminid': adminid,
                'programs': programs,
                'branches': branches,
                'years': years
            }
        )

    except Exception as e:

        print(
            "CREATE COURSE ERROR:",
            e
        )

        messages.error(
            request,
            f"Error creating course: {e}"
        )

        return redirect(
            'adminapp:manage_courses'
        )


# ============================================================
# EDIT COURSE
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_course(request, course_id):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        course = get_object_or_404(
            Course,
            id=course_id
        )

        if request.method == 'POST':

            title = request.POST.get(
                'title',
                ''
            ).strip()

            description = request.POST.get(
                'description',
                ''
            ).strip()

            program_id = request.POST.get(
                'program'
            )

            branch_id = request.POST.get(
                'branch'
            )

            year_id = request.POST.get(
                'year'
            )

            if not title or not program_id or not branch_id or not year_id:

                messages.error(
                    request,
                    "Course title, program, branch, and year are required!"
                )

                return redirect(
                    'adminapp:edit_course',
                    course_id=course_id
                )

            if Course.objects.filter(
                title=title,
                program_id=program_id,
                branch_id=branch_id,
                year_id=year_id
            ).exclude(
                id=course_id
            ).exists():

                messages.error(
                    request,
                    "A course with this title already exists for this program/branch/year combination!"
                )

                return redirect(
                    'adminapp:edit_course',
                    course_id=course_id
                )

            course.title = title

            course.description = description

            course.program_id = program_id

            course.branch_id = branch_id

            course.year_id = year_id

            course.save()

            messages.success(
                request,
                f"Course '{title}' updated successfully!"
            )

            return redirect(
                'adminapp:manage_courses'
            )

        programs = Program.objects.all().order_by(
            'program'
        )

        branches = Branch.objects.all().order_by(
            'branch'
        )

        years = Year.objects.all().order_by(
            'year'
        )

        return render(
            request,
            "edit_course.html",
            {
                'adminid': adminid,
                'course': course,
                'programs': programs,
                'branches': branches,
                'years': years
            }
        )

    except Exception as e:

        print(
            "EDIT COURSE ERROR:",
            e
        )

        return redirect(
            'nouapp:manage_courses'
        )


# ============================================================
# DELETE COURSE
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_course(request, course_id):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        course = get_object_or_404(
            Course,
            id=course_id
        )

        if request.method == 'POST':

            material_count = Material.objects.filter(
                course=course
            ).count()

            if material_count > 0:

                messages.error(
                    request,
                    f"Cannot delete course '{course.title}'. It has {material_count} materials associated with it."
                )

                return redirect(
                    'adminapp:manage_courses'
                )

            course_title = course.title

            course.delete()

            messages.success(
                request,
                f"Course '{course_title}' deleted successfully!"
            )

            return redirect(
                'adminapp:manage_courses'
            )

        return render(
            request,
            "delete_course.html",
            {
                'adminid': adminid,
                'course': course
            }
        )

    except Exception as e:

        print(
            "DELETE COURSE ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_courses'
        )


# ============================================================
# SIMPLE DELETE COURSE
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_course_simple(request, course_id):

    try:

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        course = get_object_or_404(
            Course,
            id=course_id
        )

        material_count = Material.objects.filter(
            course=course
        ).count()

        if material_count > 0:

            messages.error(
                request,
                f"Cannot delete course '{course.title}'. It has {material_count} materials associated with it."
            )

        else:

            course_title = course.title

            course.delete()

            messages.success(
                request,
                f"Course '{course_title}' deleted successfully!"
            )

        return redirect(
            'adminapp:manage_courses'
        )

    except Exception as e:

        print(
            "DELETE COURSE SIMPLE ERROR:",
            e
        )

        return redirect(
            'adminapp:manage_courses'
        )


# ============================================================
# ADMIN ENQUIRY DASHBOARD
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_enquiry_dashboard(request):

    try:

        # ----------------------------------------------------
        # CHECK ADMIN LOGIN
        # ----------------------------------------------------

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        # ----------------------------------------------------
        # GET FILTER VALUES
        # ----------------------------------------------------

        status_filter = request.GET.get(
            'status',
            ''
        )

        priority_filter = request.GET.get(
            'priority',
            ''
        )

        # ----------------------------------------------------
        # GET ALL ENQUIRIES
        # ----------------------------------------------------

        enquiries = Enquiry.objects.all().order_by(
            '-id'
        )

        # ----------------------------------------------------
        # FILTER BY STATUS
        # ----------------------------------------------------

        if status_filter:

            enquiries = enquiries.filter(
                status=status_filter
            )

        # ----------------------------------------------------
        # FILTER BY PRIORITY
        # ----------------------------------------------------

        if priority_filter:

            enquiries = enquiries.filter(
                priority=priority_filter
            )

        # ----------------------------------------------------
        # COUNTS
        # ----------------------------------------------------

        total_enquiries = Enquiry.objects.count()

        pending_enquiries = Enquiry.objects.filter(
            status='pending'
        ).count()

        in_progress_enquiries = Enquiry.objects.filter(
            status='in_progress'
        ).count()

        resolved_enquiries = Enquiry.objects.filter(
            status='resolved'
        ).count()

        closed_enquiries = Enquiry.objects.filter(
            status='closed'
        ).count()

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        context = {

            'adminid':
                adminid,

            'enquiries':
                enquiries,

            'total_enquiries':
                total_enquiries,

            'pending_enquiries':
                pending_enquiries,

            'in_progress_enquiries':
                in_progress_enquiries,

            'resolved_enquiries':
                resolved_enquiries,

            'closed_enquiries':
                closed_enquiries,

            'current_status':
                status_filter,

            'current_priority':
                priority_filter,
        }

        # ----------------------------------------------------
        # DISPLAY ADMIN ENQUIRY PAGE
        # ----------------------------------------------------

        return render(
            request,
            'admin_enquiry_dashboard.html',
            context
        )

    except Exception as e:

        print(
            "ADMIN ENQUIRY DASHBOARD ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to load enquiries."
        )

        return redirect(
            'adminapp:adminhome'
        )


# ============================================================
# ADMIN ENQUIRY DETAIL
# ============================================================

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_enquiry_detail(request, enquiry_id):

    try:

        # ----------------------------------------------------
        # CHECK ADMIN LOGIN
        # ----------------------------------------------------

        adminid = request.session.get(
            'adminid'
        )

        if not adminid:

            return redirect(
                'nouapp:login'
            )

        # ----------------------------------------------------
        # GET ENQUIRY
        # ----------------------------------------------------

        enquiry = get_object_or_404(
            Enquiry,
            id=enquiry_id
        )

        # ----------------------------------------------------
        # HANDLE POST REQUEST
        # ----------------------------------------------------

        if request.method == 'POST':

            action = request.POST.get(
                'action',
                ''
            )

            # =================================================
            # ADMIN REPLY
            # =================================================

            if action == 'reply':

                reply_message = request.POST.get(
                    'reply_message',
                    ''
                ).strip()

                # ------------------------------------------------
                # CHECK EMPTY MESSAGE
                # ------------------------------------------------

                if not reply_message:

                    messages.error(
                        request,
                        "Please enter a reply message."
                    )

                # ------------------------------------------------
                # CLOSED ENQUIRY
                # ------------------------------------------------

                elif enquiry.status == 'closed':

                    messages.warning(
                        request,
                        "This enquiry is closed. You cannot send a reply."
                    )

                else:

                    try:

                        # ------------------------------------------------
                        # CREATE / GET ADMIN USER
                        # ------------------------------------------------

                        username = f'admin_{adminid}'

                        admin_user, created = User.objects.get_or_create(

                            username=username,

                            defaults={
                                'first_name':
                                    'Administrator',

                                'is_staff':
                                    True,

                                'is_superuser':
                                    True,

                                'email':
                                    f'admin_{adminid}@nou.edu'
                            }
                        )

                        # ------------------------------------------------
                        # MAKE SURE ADMIN USER IS STAFF
                        # ------------------------------------------------

                        changed = False

                        if not admin_user.is_staff:

                            admin_user.is_staff = True

                            changed = True

                        # ------------------------------------------------
                        # MAKE SURE ADMIN USER IS SUPERUSER
                        # ------------------------------------------------

                        if not admin_user.is_superuser:

                            admin_user.is_superuser = True

                            changed = True

                        # ------------------------------------------------
                        # SET ADMIN NAME
                        # ------------------------------------------------

                        if not admin_user.first_name:

                            admin_user.first_name = 'Administrator'

                            changed = True

                        # ------------------------------------------------
                        # SAVE ADMIN USER IF CHANGED
                        # ------------------------------------------------

                        if changed:

                            admin_user.save()

                        # ------------------------------------------------
                        # CREATE ADMIN REPLY
                        # ------------------------------------------------

                        EnquiryReply.objects.create(

                            enquiry=enquiry,

                            user=admin_user,

                            message=reply_message,

                            is_admin=True
                        )

                        # ------------------------------------------------
                        # CHANGE PENDING TO IN PROGRESS
                        # ------------------------------------------------

                        if enquiry.status == 'pending':

                            enquiry.status = 'in_progress'

                            enquiry.save(
                                update_fields=[
                                    'status'
                                ]
                            )

                        messages.success(
                            request,
                            "Reply sent successfully!"
                        )

                    except Exception as e:

                        print(
                            "ADMIN REPLY ERROR:",
                            e
                        )

                        messages.error(
                            request,
                            "Unable to send the reply."
                        )

            # =================================================
            # UPDATE STATUS
            # =================================================

            elif action == 'update_status':

                new_status = request.POST.get(
                    'status',
                    ''
                )

                valid_statuses = [

                    'pending',

                    'in_progress',

                    'resolved',

                    'closed'
                ]

                if new_status not in valid_statuses:

                    messages.error(
                        request,
                        "Invalid enquiry status."
                    )

                else:

                    enquiry.status = new_status

                    enquiry.save(
                        update_fields=[
                            'status'
                        ]
                    )

                    messages.success(
                        request,
                        f"Enquiry status updated to {enquiry.get_status_display()}."
                    )

            # =================================================
            # INVALID ACTION
            # =================================================

            else:

                messages.error(
                    request,
                    "Invalid enquiry action."
                )

            # ------------------------------------------------
            # RETURN TO DETAIL PAGE
            # ------------------------------------------------

            return redirect(
                'adminapp:admin_enquiry_detail',
                enquiry_id=enquiry.id
            )

        # ----------------------------------------------------
        # GET ALL REPLIES
        # ----------------------------------------------------

        replies = EnquiryReply.objects.filter(
            enquiry=enquiry
        ).select_related(
            'user'
        ).order_by(
            'created_at'
        )

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        context = {

            'adminid':
                adminid,

            'enquiry':
                enquiry,

            'replies':
                replies,
        }

        # ----------------------------------------------------
        # DISPLAY DETAIL PAGE
        # ----------------------------------------------------

        return render(
            request,
            'admin_enquiry_detail.html',
            context
        )

    except Exception as e:

        print(
            "ADMIN ENQUIRY DETAIL ERROR:",
            e
        )

        messages.error(
            request,
            "Unable to open this enquiry."
        )

        return redirect(
            'adminapp:admin_enquiry_dashboard'
        )
