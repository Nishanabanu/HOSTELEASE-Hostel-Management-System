from django.shortcuts import render, HttpResponse, redirect,get_object_or_404
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from django.contrib import messages



def logout(request):
    request.session.flush()
    return redirect('kmct_home')

def kmct_home(request):
    wardens = Warden.objects.all()

    context = {
        'wardens': wardens,
    }
    
    return render(request, 'kmct/kmct_home_page.html', context)
    
def kmct_login_page(request):
    return render(request, 'kmct/kmct_login_page.html')

def kmct_about_page(request):
    return render(request, 'kmct/kmct_about_page.html')

def kmct_gallery_page(request):
    return render(request, 'kmct/kmct_gallery_page.html')

def admin_home(request):
    return render(request, 'admin/admin_home.html')

def student_home(request):
    student = Student.objects.get(LOGIN__id=request.session['lid'])
    return render(request, 'student/student_home.html',{'student':student})

def warden_home(request):
    return render(request, 'warden/warden_home.html')

def tutor_home(request):
    return render(request, 'tutor/tutor_home.html')

def parent_home(request):
    return render(request, 'parent/parent_home.html')


def user_login(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        
        login_fetch = LoginTable.objects.filter(user_name=user_name, password=password)
        if login_fetch.exists():
            login_objects = LoginTable.objects.get(user_name=user_name, password=password)
            request.session['lid'] = login_objects.id
            
            user_role = login_objects.role
            
            # Get the user's full name based on their role
            if user_role == 'student':
                student = Student.objects.get(LOGIN_id=request.session['lid'])
                request.session['student_name'] = student.name
            elif user_role == 'warden':
                warden = Warden.objects.get(LOGIN_id=request.session['lid'])
                request.session['warden_name'] = warden.name
            elif user_role == 'tutor':
                tutor = Tutor.objects.get(LOGIN_id=request.session['lid'])
                request.session['tutor_name'] = tutor.name
            elif user_role == 'parent':
                parent = Parent.objects.get(LOGIN_id=request.session['lid'])
                request.session['parent_name'] = parent.name

            if user_role == 'admin':
                return redirect("/admin_home")
            elif user_role == 'warden':
                return redirect("/warden_home")
            elif user_role == 'tutor':
                return redirect("/tutor_home")
            elif user_role == 'parent':
                return redirect("/parent_home")
            elif user_role == 'student':
                return redirect("/student_home")
            elif user_role == 'pending':
                return HttpResponse('''<script>alert("Your Account is not active, Contact Warden"); window.location = "/";</script>''')
            elif user_role == 'blocked':
                return HttpResponse('''<script>alert("Your Account is Blocked, Contact Warden"); window.location = "/";</script>''')
            else:
                return HttpResponse('''<script>alert("Invalid"); window.location = "/";</script>''')
        else:
            return HttpResponse('''<script>alert("Invalid"); window.location = "/";</script>''')
    else:
        return render(request, 'kmct/kmct_login_page.html')      

   
#---------------------------------------------------------------------------------------------------------------------------------   
# @login_required(login_url='/')    
def admin_view_hostel(request):
    assigned_hostels = Warden.objects.all()  # Hostels with assigned wardens
    unassigned_hostels = Hostel.objects.filter(warden__isnull=True)  # Hostels without assigned wardens
    return render(request, 'admin/admin_view_hostel.html', {
        'assigned_hostels': assigned_hostels,
        'unassigned_hostels': unassigned_hostels
    })

# @login_required(login_url='/')    
def admin_add_hostel(request):
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        details = request.POST['address']
        status = request.POST['status']
        image = request.FILES['image']
        
        hostel = Hostel.objects.create(name=name, number=number, details=details, status=status, image=image)
        
        # Get selected courses as a list of IDs
        selected_courses = request.POST.getlist('courses')
        
        # Set the many-to-many relationship
        hostel.COURSE.set(selected_courses)
        hostel.save()

        return render(request, 'admin/admin_add_hostel.html', {'success': True})
    
    courses = Course.objects.all()
    return render(request, 'admin/admin_add_hostel.html', {'courses': courses})


# def admin_delete_hostel(request,id):
#     hostel = Hostel.objects.get(id=id)
#     hostel.delete()
#     return HttpResponse('''<script>alert("Deleted successfully");window.location="/admin_view_hostel"</script>''')

# @login_required(login_url='/')
def admin_edit_hostel(request, id):
    hostel = get_object_or_404(Hostel, id=id)

    if request.method == 'POST':
        hostel.name = request.POST.get('name')
        hostel.number = request.POST.get('number')
        hostel.details = request.POST.get('address')
        hostel.status = request.POST.get('status')

        if 'image' in request.FILES:
            hostel.image = request.FILES['image']
        
        # Update the courses accepted by this hostel
        selected_courses = request.POST.getlist('courses')
        hostel.COURSE.set(selected_courses)
        
        hostel.save()
        return render(request, 'admin/admin_edit_hostel.html', {'hostel': hostel, 'success': True, 'courses': Course.objects.all()})

    courses = Course.objects.all()
    return render(request, 'admin/admin_edit_hostel.html', {'hostel': hostel, 'courses': courses})

#--------------------------------------------------------------------------------------------------------------------------------- 
# @login_required(login_url='/')   
def admin_view_wardens(request):
    warden_details = Warden.objects.all()
    return render(request, 'admin/admin_view_wardens.html',{'warden_details':warden_details})

# @login_required(login_url='/')
def admin_add_warden(request):
    # Fetch hostels that are not assigned to any warden
    available_hostels = Hostel.objects.filter(warden__isnull=True)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        image = request.FILES.get('image')
        hostel_id = request.POST.get('hostel')
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')

        # Save warden login details in the LoginTable
        warden_login_details = LoginTable.objects.create(
            user_name=user_name,
            password=password,
            role='warden'
        )
        warden_login_details.save()

        # Fetch the selected hostel object
        hostel = Hostel.objects.get(id=hostel_id)

        # Save warden profile details in the Warden model
        warden_profile_details = Warden.objects.create(
            LOGIN=warden_login_details,
            name=name,
            phone=phone,
            address=address,
            image=image,
            HOSTEL=hostel
        )
        warden_profile_details.save()

        return render(request, 'admin/admin_add_warden.html', {'success': True, 'hostels': available_hostels})
    return render(request, 'admin/admin_add_warden.html', {'hostels': available_hostels})

# @login_required(login_url='/')
def admin_edit_warden(request, id):
    warden = Warden.objects.get(id=id)
    login = warden.LOGIN
    if request.method == 'POST':
        warden.name = request.POST.get('name')
        warden.phone = request.POST.get('phone')
        warden.address = request.POST.get('address')
        login.user_name = request.POST.get('user_name')
        login.password = request.POST.get('password')
        
        if 'image' in request.FILES:
            warden.image = request.FILES['image']
        warden.save()
        login.save()
        return render(request, 'admin/admin_edit_warden.html', {'warden': warden, 'success': True})
    return render(request, 'admin/admin_edit_warden.html', {'warden': warden})

# def admin_delete_warden(request,id):
#     warden = Warden.objects.get(id=id)
#     login_id = warden.LOGIN_id
#     warden.delete()
#     LoginTable.objects.filter(id=login_id).delete()
#     return HttpResponse('''<script>alert("Deleted successfully");window.location="/admin_view_wardens"</script>''')

#---------------------------------------------------------------------------------------------------------------------------------
# @login_required(login_url='/')
def admin_view_departments(request):
    departments = Department.objects.all()
    return render(request, 'admin/admin_view_departments.html', {'departments': departments})
    
# @login_required(login_url='/')  
def admin_add_departments(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        department = Department.objects.create(
            name=name,
            image=image
        )
        department.save()
        return render(request, 'admin/admin_add_departments.html', {'success': True})
    return render(request, 'admin/admin_add_departments.html')

# @login_required(login_url='/')
def admin_edit_department(request, id):
    department = Department.objects.get(id=id)
    if request.method == 'POST':
        department.name = request.POST.get('name')
        if 'image' in request.FILES:
            department.image = request.FILES['image']
        department.save()
        return render(request, 'admin/admin_edit_department.html', {'department': department, 'success': True})
    return render(request, 'admin/admin_edit_department.html', {'department': department})


 
#---------------------------------------------------------------------------------------------------------------------------------   
# @login_required(login_url='/')    
def admin_view_courses(request):
    courses = Course.objects.all()
    return render(request, 'admin/admin_view_courses.html', {'courses': courses})

# @login_required(login_url='/')
def admin_add_course(request):
    departments = Department.objects.all() 
    if request.method == 'POST':
        department_id = request.POST.get('department')
        course_name = request.POST.get('course_name')
        course_type = request.POST.get('type')
        duration = request.POST.get('duration')
        
        department = Department.objects.get(id=department_id) 
        
        course = Course.objects.create(
            DEPARTMENT=department,
            course_name=course_name,
            type=course_type,
            duration=duration
        )
        course.save()
        return render(request, 'admin/admin_add_course.html', {'success': True, 'departments': departments})
    return render(request, 'admin/admin_add_course.html', {'departments': departments})

# @login_required(login_url='/')        
def admin_edit_course(request, id):
    course = get_object_or_404(Course, id=id)
    departments = Department.objects.all()
    
    if request.method == 'POST':
        department_id = request.POST.get('department')
        course_name = request.POST.get('course_name')
        course_type = request.POST.get('type')
        duration = request.POST.get('duration')
        
        department = Department.objects.get(id=department_id)
        
        course.DEPARTMENT = department
        course.course_name = course_name
        course.type = course_type
        course.duration = duration
        course.save()
        
        return render(request, 'admin/admin_edit_course.html', {'course': course, 'departments': departments, 'success': True})
    return render(request, 'admin/admin_edit_course.html', {'course': course, 'departments': departments})
    
# @login_required(login_url='/')
def admin_view_tutors(request):
    tutors = Tutor.objects.all()
    return render(request, 'admin/admin_view_tutors.html', {'tutors':tutors})

# @login_required(login_url='/')   
def admin_add_tutor(request):
    if request.method == "POST":
        name = request.POST.get('tutor_name')
        id_number = request.POST.get('tutor_id')
        year = request.POST.get('year')
        phone_number = request.POST.get('tutor_phone')
        image = request.FILES.get('image')
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        course_id = request.POST.get('course')
            

        tutor_login_details = LoginTable.objects.create(
            user_name=user_name,
            password=password,
            role='tutor'
        )

        # Fetch the selected course details
        course_details = Course.objects.get(id=course_id)

        # Create the Tutor profile
        Tutor.objects.create(
            LOGIN=tutor_login_details,
            COURSE=course_details,
            name=name,
            year=year,
            phone_number=phone_number,
            image=image,
            id_number=id_number
        )

        return redirect('admin_view_tutors')  # Redirect to the tutor list page after saving

    # Fetch all departments to display in the dropdown
    departments = Department.objects.all()
    return render(request, 'admin/admin_add_tutor.html', {'departments': departments})

# @login_required(login_url='/')
def get_courses(request):
    department_id = request.GET.get('department_id')
    courses = Course.objects.filter(DEPARTMENT_id=department_id).values('id', 'course_name')
    return JsonResponse(list(courses), safe=False)

# @login_required(login_url='/')   
def admin_edit_tutor(request, id):
    tutor_details = get_object_or_404(Tutor, id=id)
    departments = Department.objects.all()
    courses = Course.objects.filter(DEPARTMENT=tutor_details.COURSE.DEPARTMENT)

    if request.method == "POST":
        tutor_details.name = request.POST.get('name')
        tutor_details.id_number = request.POST.get('id_number')
        tutor_details.year = request.POST.get('year')
        tutor_details.phone_number = request.POST.get('phone_number')
        tutor_details.LOGIN.user_name = request.POST.get('user_name')
        tutor_details.LOGIN.password = request.POST.get('password')
        
        if request.FILES.get('image'):
            tutor_details.image = request.FILES['image']
        
        course_id = request.POST.get('course_id')
        if course_id:
            selected_course = get_object_or_404(Course, id=course_id)
            tutor_details.COURSE = selected_course
        
        tutor_details.LOGIN.save()
        tutor_details.save()
        
        return render(request, 'admin/admin_edit_tutor.html', {
            'tutor': tutor_details,
            'departments': departments,
            'courses': Course.objects.filter(DEPARTMENT=tutor_details.COURSE.DEPARTMENT),
            'success': True,
        })
    
    return render(request, 'admin/admin_edit_tutor.html', {
        'tutor': tutor_details,
        'departments': departments,
        'courses': courses,
    })

# @login_required(login_url='/')
def get_courses_by_department(request):
    department_id = request.GET.get('department_id')
    courses = Course.objects.filter(DEPARTMENT_id=department_id)
    course_list = [{'id': course.id, 'course_name': course.course_name} for course in courses]
    return JsonResponse({'courses': course_list})
    
# @login_required(login_url='/')
def admin_manage_complaints(request):
    complaints = Complaint.objects.all()
    return render(request, "admin/admin_view_complaints.html",{"complaints":complaints})

# @login_required(login_url='/')
def admin_reply_complaint(request,id):
    complaint_object = get_object_or_404(Complaint, id=id)
    if request.method == "POST":
        reply = request.POST.get('complaint_reply')
        complaint_object.reply = reply
        complaint_object.replied_status = True
        complaint_object.save()
        return redirect('admin/admin_view_complaints.html')  # Redirect to the complaints list after replying
    return render(request, 'admin/admin_reply_complaint.html', {'complaint_object': complaint_object})
        
# @login_required(login_url='/')   
def admin_view_payments(request):
    payments = Payment.objects.all()
    return render(request, 'admin/admin_view_payments.html',{'payments':payments})

# @login_required(login_url='/')
def admin_send_payment_request(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payments = Payment.objects.filter(status='Pending')
        notification = Notification.objects.create(
            notification = "THE HOSTEL FEES PAGE IS LIVE NOW TO MAKE PAYMENTS",
            user_type = 'student'
        )
        notification.save()
        
        for payment in payments:
            payment.amount = amount 
            payment.is_requested = True
            payment.save()
        return redirect("/admin_view_payments")
    return render(request, 'admin/admin_view_payments.html')
    
# @login_required(login_url='/')
def admin_send_notification(request):
    if request.method == 'POST':
        notification_text = request.POST.get('notification')
        user_type = request.POST.get('user_type')
        
        Notification.objects.create(
            notification=notification_text,
            user_type=user_type
        )
        return redirect("/admin_home")
    return render(request, 'admin/admin_send_notification.html')
   
# @login_required(login_url='/')        
def admin_view_students(request):
    student_details = Room.objects.filter(STUDENT__COURSE__duration__in=[1, 3])
    return render(request, 'admin/admin_view_students.html', {'student_details': student_details})

# @login_required(login_url='/')
def admin_view_alumini(request):
    alumini_details = Room.objects.filter(STUDENT__COURSE__duration__gt=3)
    return render(request, 'admin/admin_view_alumini.html', {'alumini_details': alumini_details})

#-------------------------------------------------------------------------------------------------------------------------------------

def warden_view_profile(request):
    warden_id = request.session.get('lid')
    login_objects = LoginTable.objects.get(id=warden_id)
    warden_profile = Warden.objects.get(LOGIN=login_objects)
    return render(request, 'warden/warden_view_profile.html',{'warden_profile':warden_profile})


def warden_edit_profile(request):
    warden_id = request.session.get('lid')
    if not warden_id:
        return HttpResponse('Warden ID not found in session.')

    warden = Warden.objects.get(LOGIN__id=warden_id)

    if request.method == 'POST':
        warden.name = request.POST.get('name')
        warden.phone = request.POST.get('phone')
        warden.address = request.POST.get('address')

        if 'image' in request.FILES:
            warden.image = request.FILES['image']

        warden.save()
        return redirect("/warden_view_profile")
    return render(request, 'warden/warden_edit_profile.html', {'warden': warden})

def warden_change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        new_username = request.POST.get('username')
        
        credentials = LoginTable.objects.filter(id=request.session['lid'], password=old_password)
        if credentials.exists():
            if new_password==confirm_password:
                new_credentials = credentials.update(password=confirm_password,user_name=new_username)        
                if new_credentials:
                    return HttpResponse('''<script>alert("User Name and Password Changed"); window.location="/warden_home";</script>''')
                else:
                    return HttpResponse('''<script>alert("Failed to change password"); window.location="/warden_change_password";</script>''')
            else:
                return HttpResponse('''<script>alert("New password and confirm password do not match"); window.location="/warden_change_password";</script>''')
        else:
            return HttpResponse('''<script>alert("Invalid old password"); window.location="/warden_change_password";</script>''')
    return render(request, 'warden/warden_change_password.html')

def warden_verify_student(request):
    warden = get_object_or_404(Warden, LOGIN=request.session['lid'])
    hostel = warden.HOSTEL
    
    # Fetching all students related to the hostel's courses
    students = Student.objects.filter(COURSE__in=hostel.COURSE.all())
    
    # Get filter parameters from request
    search_course = request.GET.get('course', '')
    search_department = request.GET.get('department', '')
    
    # Filter students based on search criteria
    if search_course:
        students = students.filter(COURSE__course_name__icontains=search_course)
    if search_department:
        students = students.filter(COURSE__DEPARTMENT__name__icontains=search_department)

    # Fetch all courses and departments for the filter dropdowns
    courses = hostel.COURSE.all()
    departments = Department.objects.filter(course__in=courses).distinct()

    return render(request, 'warden/warden_verify_students.html', {
        'students': students,
        'courses': courses,
        'departments': departments,
        'search_course': search_course,
        'search_department': search_department,
    })

    
def warden_accept_reject_student(request):
    action = request.POST['action']
    login_id = request.POST['login_id']

    login_obj = LoginTable.objects.get(id=login_id)

    if action == 'accept':
        login_obj.role = 'student'
    elif action == 'reject':
        login_obj.role = 'pending'

    login_obj.save()
    return redirect("/warden_verify_student")

def warden_block_unblock_student(request):
    action = request.POST['action']
    login_id = request.POST['login_id']

    login_obj = LoginTable.objects.get(id=login_id)

    if action == 'block':
        login_obj.role = 'blocked'
    elif action == 'unblock':
        login_obj.role = 'student'
    login_obj.save()
    return HttpResponse(f'<script>alert("Status updated to {login_obj.role}"); window.location="/warden_verify_student";</script>')

    

def warden_add_new_room(request):
    warden = Warden.objects.get(LOGIN_id=request.session['lid']) 
    hostel = warden.HOSTEL 
    if request.method == "POST":
        room_number = request.POST['room_number']
        capacity = request.POST['capacity']
        image = request.FILES['image']
        
        room = Room.objects.create(
            room_number=room_number,
            capacity=capacity,
            image=image,
            HOSTEL=hostel  
        )
        room.save()
        return redirect('/warden_view_rooms')
    return render(request, 'warden/warden_add_new_room.html')

def warden_edit_room(request,room_id):
    warden = Warden.objects.get(LOGIN_id=request.session['lid']) 
    hostel = warden.HOSTEL 
    room = Room.objects.get(id=room_id,HOSTEL=hostel)
    if request.method == 'POST':
        room.room_number=request.POST['room_number']
        room.capacity=request.POST['capacity']
        
        if 'image' in request.FILES:
            room.image=request.FILES['image']
            
        room.save()
        return redirect('/warden_view_rooms')
    return render(request, 'warden/warden_edit_room.html',{'room':room})



def warden_view_rooms(request):
    warden = get_object_or_404(Warden, LOGIN_id=request.session['lid'])
    hostel = warden.HOSTEL
    room_list = Room.objects.filter(HOSTEL=hostel)

    # Get all available students not assigned to any room
    assigned_students = Student.objects.filter(rooms__isnull=False).distinct()
    available_students = Student.objects.filter(COURSE__in=hostel.COURSE.all(),LOGIN__role='student').exclude(id__in=assigned_students)

    context = {
        'room_list': room_list,
        'available_students': available_students,
    }
    return render(request, 'warden/warden_view_rooms.html', context)


def assign_student_to_room(request, student_id, room_id):
    student = Student.objects.get(id=student_id, LOGIN__role='student')
    room = Room.objects.get(id=room_id)

    # Check if the student is already assigned to a room
    if student.rooms.exists():
        return HttpResponse("Student is already assigned to a room.", status=400)

    # Check if the hostel accepts the student's course
    if room.HOSTEL.COURSE.filter(id=student.COURSE.id).exists():
        # Check if there's enough capacity in the room
        if room.capacity > 0:
            room.STUDENTS.add(student)
            room.capacity -=1
            room.save()
            return redirect('warden_view_rooms')
        else:
            return HttpResponse("No available capacity in this room.", status=400)
    else:
        return HttpResponse("Student's course is not accepted by this hostel.", status=400)


def remove_student_from_room(request, student_id, room_id):
    student = get_object_or_404(Student, id=student_id)
    room = get_object_or_404(Room, id=room_id)

    # Check if the student is assigned to the room
    if student in room.STUDENTS.all():
        room.STUDENTS.remove(student)
        room.capacity += 1  
        room.save()
        return redirect('warden_view_rooms')
    else:
        return HttpResponse("Student is not assigned to this room.", status=400)


def tutor_view_students(request):
    tutor = Tutor.objects.get(LOGIN=request.session['lid'])  # Assuming user is logged in as a tutor
    students = Student.objects.filter(COURSE=tutor.COURSE, year=tutor.year)  # Matching course and year
    
    context = {
        'students': students,
        'tutor_name': tutor.name,
    }
    
    return render(request, 'tutor/tutor_view_students.html', context)

def assign_parent(request, id):
    student = Student.objects.get(id=id)  # Get the student by ID

    if request.method == 'POST':
        parent_name = request.POST.get('parent_name')  
        phone_number = request.POST.get('phone_number')
        user_name = request.POST.get('user_name') 
        password = request.POST.get('password')  
        
        login = LoginTable(
            user_name=user_name,
            password=password,
            role='parent'
        )
        login.save()
        
        parent = Parent(
            LOGIN=login, 
            STUDENT=student,
            name=parent_name,
            phone_number=phone_number
        )
        parent.save()
        return redirect('/tutor_view_students')  # Redirect back to the students view
    return render(request, 'tutor/assign_parent.html', {'student': student})

        
def tutor_view_profile(request):
    tutor_id = request.session['lid']  # Get the login ID from session
    login = LoginTable.objects.get(id=tutor_id)
    tutor = Tutor.objects.get(LOGIN=login)  # Retrieve the tutor's profile
    return render(request, 'tutor/tutor_view_profile.html', {'tutor': tutor})

def tutor_edit_profile(request):
    tutor_id = request.session['lid']  # Get the login ID from session
    login = LoginTable.objects.get(id=tutor_id)
    tutor = Tutor.objects.get(LOGIN=login) 
    
    if request.method == 'POST':
        tutor.name = request.POST.get('name')
        tutor.phone_number = request.POST.get('phone_number')
        
        if 'image' in request.FILES:
            tutor.image = request.FILES['image']
        tutor.save()
        return redirect('/tutor_view_profile')  # Redirect back to view profile after saving
    return render(request, 'tutor/edit_profile.html', {'tutor': tutor})
            
    


def parent_view_profile(request):
    parent_id = request.session['lid']  # Get the login ID from session
    login = LoginTable.objects.get(id=parent_id)
    parent = Parent.objects.get(LOGIN=login)  # Retrieve the parent's profile
    student = parent.STUDENT  # Get the associated student
    return render(request, 'parent/parent_view_profile.html', {'parent': parent, 'student': student})

def parent_edit_profile(request):
    parent_id = request.session['lid']  # Get the login ID from session
    login = LoginTable.objects.get(id=parent_id)
    parent = Parent.objects.get(LOGIN=login)

    if request.method == 'POST':
        parent.name = request.POST.get('name')
        parent.phone_number = request.POST.get('phone_number')
        parent.save()  # Save the changes
        return redirect('parent_view_profile')  # Redirect to the profile view

    return render(request, 'parent/parent_edit_profile.html', {'parent': parent})


def student_registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if LoginTable.objects.filter(user_name=username,password=password).exists():
            return HttpResponse('''<script>alert("Credentials already exists"); window.location="/";</script>''')
        student_login_details = LoginTable.objects.create(
            user_name=username,
            password=password,
            role='pending'
        )
        student_login_details.save()
        
        # Fetch the selected course
        course_id = request.POST['course']
        course_details = Course.objects.get(id=course_id)
        
        name = request.POST['name']
        number = request.POST['number']
        address = request.POST['address']
        dob = request.POST['dob']
        image = request.FILES['image']
        parent_phone_number = request.POST['parent_phone_number']
        academic_year = request.POST['academic_year']
        admission_number = request.POST['admission_number']
        
        student_details = Student.objects.create(
            LOGIN=student_login_details,
            COURSE=course_details,
            name=name,
            number=number,
            address=address,
            dob=dob,
            year=academic_year,  
            image=image,
            parent_phone_number=parent_phone_number,
            admission_number=admission_number
        )
        student_details.save()
        return HttpResponse('''<script>alert("Registration Successfully Completed"); window.location="/";</script>''')
    courses = Course.objects.all()
    return render(request, 'student/student_registration.html', {'courses': courses})

def student_view_profile(request):
    student_id = request.session['lid']  # Assuming the student ID is stored in the session
    login = LoginTable.objects.get(id=student_id)
    student = Student.objects.get(LOGIN=login)  # Retrieve the student's profile
    course = student.COURSE  # Get the course the student is enrolled in
    
    # Retrieve the tutor based on the student's course and year
    try:
        tutor = Tutor.objects.get(COURSE=course, year=student.year)
    except Tutor.DoesNotExist:
        tutor = None  # In case no tutor is assigned for this course and year
    
    # Pass student, course, and tutor details to the template
    return render(request, 'student/student_view_profile.html', {
        'student': student,
        'course': course,
        'tutor': tutor,
    })


def student_update_profile(request):
    student_id = request.session['lid']  # Get the student ID from session
    student = Student.objects.get(LOGIN__id=student_id)  # Retrieve the student's profile
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.number = request.POST.get('number')
        student.address = request.POST.get('address')
        student.dob = request.POST.get('dob')
        student.parent_phone_number = request.POST.get('parent_phone_number')

        if 'image' in request.FILES:
            student.image = request.FILES['image']

        student.save()
        return HttpResponse('''<script>alert("Profile Updated Successfully"); window.location="/student_view_profile";</script>''')
    return render(request, 'student/student_edit_profile.html', {'student': student})

def student_manage_leave(request):
    student_id = request.session['lid']
    leave = LeavingRegister.objects.filter(STUDENT__LOGIN_id=student_id)
    return render(request, 'student/manage_leave.html',{'leave':leave})

def add_leave(request):
    student_id = request.session['lid']
    student = Student.objects.get(LOGIN_id=student_id)

    try:
        tutor = Tutor.objects.get(COURSE=student.COURSE, year=student.year)
    except Tutor.DoesNotExist:
        tutor = None  # Handle case where no tutor is found

    if request.method == "POST":
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        reason = request.POST['reason']

        leave = LeavingRegister.objects.create(
            STUDENT=student,
            TUTOR=tutor,  
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status='pending'  
        )
        return redirect('/student_manage_leave')  
    return render(request, 'student/add_new_leave.html')

def manage_local_movement(request):
    student_id = request.session['lid']
    student = Student.objects.get(LOGIN_id=student_id)

    if request.method == "POST":
        exit_time_str = request.POST.get('exit_time')
        reason = request.POST.get('reason')

        try:
            exit_time = datetime.strptime(exit_time_str, '%H:%M').time()

            LocalMovement.objects.create(
                STUDENT=student,
                exit_time=exit_time,
                entry_time=None,  # Set to None initially
                reason=reason
            )
            return redirect('manage_local_movement')

        except ValueError:
            error_message = "Invalid time format. Please use HH:MM."
            local_movements = LocalMovement.objects.filter(STUDENT=student)
            return render(request, 'student/manage_local_movement.html', {
                'local_movements': local_movements,
                'student': student,
                'error_message': error_message
            })

    local_movements = LocalMovement.objects.filter(STUDENT=student)

    return render(request, 'student/manage_local_movement.html', {
        'local_movements': local_movements,
        'student': student
    })


def update_entry_time(request, movement_id):
    movement = get_object_or_404(LocalMovement, id=movement_id)

    if request.method == "POST":
        entry_time_str = request.POST.get('entry_time')

        try:
            entry_time = datetime.strptime(entry_time_str, '%H:%M').time()
            if entry_time < movement.exit_time:
                error_message = "Entry time cannot be less than exit time."
                return render(request, 'student/update_entry_time.html', {
                    'movement': movement,
                    'error_message': error_message
                })

            movement.entry_time = entry_time
            movement.save()
            return redirect('manage_local_movement')  # Redirect to the management page

        except ValueError:
            error_message = "Invalid time format. Please use HH:MM."
            return render(request, 'student/update_entry_time.html', {
                'movement': movement,
                'error_message': error_message
            })
    return render(request, 'student/update_entry_time.html', {'movement': movement})


def delete(request,id):
    movement = get_object_or_404(LocalMovement, id=id)
    movement.delete()
    return redirect('manage_local_movement')
