# Django core imports
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.db.models import Q

# Django utilities
from django.utils import timezone
from django.utils.timezone import now

# Third-party imports
import csv

# Standard library imports
from datetime import timedelta

# Application-specific imports
from .locations import locations
from PassApp.models import HallPass
from .tasks import expire_hall_pass
from .utils import (
    is_valid_location, hall_pass_to_dict, is_staff_or_admin, 
    is_student_member, matches_nonce, no_nonce
)

# Create your views here.

def user_login(request):
    # Check if user is already logged in
    if request.user.is_authenticated:
        has_pass = HallPass.objects.filter(Q(student=request.user) & (Q(status='Active') | Q(status='Expired'))).exists()
        if has_pass:
            return redirect('passapp-pass')
        else:
            return redirect('passapp-dashboard')
    
    if request.method == 'POST':
        username = no_nonce(request.POST.get('userid'))
        username_with_nonce = request.POST.get('userid')
        if not username:
            return render(request, 'PassApp/login.html', {
                'error_message': "Empty User ID."
            })
        if not username.isdigit():
            return render(request, 'PassApp/login.html', {
                'error_message': "Only numbers allowed, please try again."
            })
        
        user = authenticate(request, username=username)
        if user:
            group_names = [group.name for group in user.groups.all()]

            if user.is_superuser or user.is_staff:
                return render(request, 'PassApp/login.html', {
                    'error_message': "Cannot login as superuser on this page, use administrator page."
                })
            elif 'student' in group_names or 'staff' in group_names or 'admin' in group_names:
                if 'staff' in group_names or 'admin' in group_names:
                    if not matches_nonce(username_with_nonce):
                        return render(request, 'PassApp/login.html', {
                            'error_message': "Invalid User ID, please try again."
                        })
                login(request, user)
                return redirect('passapp-dashboard')
            else:
                return render(request, 'PassApp/login.html', {
                    'error_message': "Could not find valid user role, please report this error."
                })
        else:
            return render(request, 'PassApp/login.html', {
                'error_message': "Invalid User ID, please try again."
            })

    easter_egg = timezone.localtime(timezone.now())
    if easter_egg.hour == 0 and easter_egg.minute == 1:
        return render(request, 'PassApp/login.html', {
            'error_message': '<a href="https://unix.stackexchange.com/questions/405783/why-does-man-print-gimme-gimme-gimme-at-0030" style="color: white;"> Gimme Gimme Gimme a man after midnight. </a>'
        })
    return render(request, 'PassApp/login.html')

@login_required
def dashboard(request):
    group_names = [group.name for group in request.user.groups.all()]
    user = request.user
    valid_times = [90, 60, 30, 10, 5]
    context = { 
        'valid_times': valid_times, 
        'locations': locations,
    }
    # Ensures the user is logged in and sends them to the right dashboard
    if user.is_superuser or user.is_staff:
        logout(request)
        return redirect('passapp-login')
    elif 'student' in group_names:
        has_pass = HallPass.objects.filter(Q(student=request.user) & (Q(status='Active') | Q(status='Expired'))).exists()
        if has_pass:
            return redirect('passapp-pass')
        
        if request.method == 'POST':
            # Get information from client
            selected_time = request.POST.get('selected-time', None)
            building_from = request.POST.get('building-from', None)
            room_from = request.POST.get('room-from', None)
            building_to = request.POST.get('building-to', None)
            room_to = request.POST.get('room-to', None)
            staff_pin_no_nonce = no_nonce(request.POST.get('teacher-pin', None))
            staff_pin = request.POST.get('teacher-pin', None)
            staff = authenticate(request, username=staff_pin_no_nonce)

            context.update({
                'submitted_data': {
                    'selected_time': selected_time,
                    'building_from': building_from,
                    'room_from': room_from,
                    'building_to': building_to,
                    'room_to': room_to,
                }
            })

            # Combine building and room values to represent full locations
            location_from = f"{building_from} {room_from}"
            location_to = f"{building_to} {room_to}"

            # Validate if the user has an invalid location or destination
            if not (is_valid_location(building_from, room_from) and is_valid_location(building_to, room_to)):
                context['error_message'] = "Invalid building or room selection."
                return render(request, 'PassApp/studentdashboard.html', context)
            
            # Check if the starting location is a bathroom
            if room_from.lower() == 'bathroom':
                context['error_message'] = "Cannot create a pass from the bathroom."
                return render(request, 'PassApp/studentdashboard.html', context)

            # Check if the starting location is the same as the destination
            if location_from == location_to:
                context['error_message'] = "Your destination cannot be the same as your starting location."
                return render(request, 'PassApp/studentdashboard.html', context)

            # Ensure a valid time was selected
            if not selected_time or int(selected_time) not in valid_times:
                context['error_message'] = "No time selected."
                return render(request, 'PassApp/studentdashboard.html', context)
            
            if not staff_pin:
                context['error_message'] = "No staff pin provided."
                return render(request, 'PassApp/studentdashboard.html', context)
            
            if not staff_pin.isdigit():
                context['error_message'] = "Only numbers allowed in pin field, please try again."
                return render(request, 'PassApp/studentdashboard.html', context)

            if staff is not None and is_staff_or_admin(staff) and matches_nonce(staff_pin):
                # Create Pass
                hall_pass = HallPass.objects.create(
                    student=request.user,
                    staff=staff,
                    building_from=building_from,
                    room_from=room_from,
                    building_to=building_to,
                    room_to=room_to,
                    status='Active',
                    duration=int(selected_time),
                )
                expire_hall_pass.apply_async((hall_pass.id,), countdown=hall_pass.duration * 60)
                return redirect('passapp-pass')
            else:
                context['error_message'] = "Invalid teacher pin."
                return render(request, 'PassApp/studentdashboard.html', context)
        return render(request, 'PassApp/studentdashboard.html', context)
    elif 'admin' in group_names:
        return render(request, 'PassApp/admindashboard.html', context)
    elif 'staff' in group_names:
        return render(request, 'PassApp/staffdashboard.html', context)
    else:
        return HttpResponse("You do not have the Student, Staff, or Admin roles, please report this error to us!")

@user_passes_test(is_student_member, login_url='passapp-login')
def pass_screen(request):
    hall_passes = HallPass.objects.filter(Q(student=request.user) & (Q(status='Active') | Q(status='Expired')))

    if not hall_passes.exists():
        return redirect('passapp-dashboard')

    context = {
        'passes': hall_passes,
    }

    return render(request, 'PassApp/passscreen.html', context)



# User Actions (not items visible to the user)

@login_required
def end_pass(request, pass_id):
    user = request.user
    if user.groups.filter(name='student').exists():
        hall_pass = HallPass.objects.get(id=pass_id, student=request.user)
    elif user.groups.filter(name='staff').exists():
        hall_pass = HallPass.objects.get(id=pass_id, staff=request.user)
    hall_pass.status = 'Ended'
    hall_pass.save()
    return redirect('passapp-dashboard')

@login_required
def json_passes(request):
    user = request.user

    if user.groups.filter(name='student').exists():
        passes = HallPass.objects.filter(Q(student=user) & (Q(status='Active') | Q(status='Expired')))
    elif user.groups.filter(name='admin').exists():
        one_week_ago = now() - timedelta(days=7)
        passes = HallPass.objects.filter(start_time__gte=one_week_ago).order_by('-start_time')
    elif user.groups.filter(name='staff').exists():
        passes = HallPass.objects.exclude(status='Ended').filter(staff=user).order_by('-start_time')
    else:
        passes = []

    # Convert passes to dictionaries
    passes_data = [hall_pass_to_dict(hall_pass) for hall_pass in passes]

    # Create JSON response
    return JsonResponse({
        'passes': passes_data,
    })

@user_passes_test(is_staff_or_admin, login_url='passapp-login')
def download_passes(request):
    user = request.user

    if user.groups.filter(name='admin').exists():
        passes = HallPass.objects.order_by('-start_time')
    elif user.groups.filter(name='staff').exists():
        passes = HallPass.objects.filter(staff=user).order_by('-start_time')
    else:
        passes = []

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename=passes_{timezone.now().strftime("%Y-%m-%d")}.csv'},
    )

    writer = csv.writer(response)
    header = ['id', 'student_name', 'staff_name', 'status', 'building_from', 'room_from', 'building_to', 'room_to', 'duration', 'start_time']
    writer.writerow(header)

    # Write the data rows
    for hall_pass in passes:
        writer.writerow([
            hall_pass.id,
            hall_pass.student.get_full_name(),
            hall_pass.staff.get_full_name(),
            hall_pass.status,
            hall_pass.building_from,
            hall_pass.room_from,
            hall_pass.building_to,
            hall_pass.room_to,
            hall_pass.duration,
            hall_pass.start_time,
        ])

    return response

@login_required
@require_http_methods(["GET"])
def pass_status(request, pass_id):
    try:
        hall_pass = HallPass.objects.get(
            Q(id=pass_id) & (Q(student=request.user) | Q(staff=request.user))
        )
        current_time = now()
        end_time = hall_pass.start_time + timedelta(minutes=hall_pass.duration)
        total_seconds = int((end_time - current_time).total_seconds())
        
        if total_seconds <= 0:
            remaining_minutes = 0
            remaining_seconds = 0
        else:
            remaining_minutes = total_seconds // 60
            remaining_seconds = total_seconds % 60

        data = {
            'status': hall_pass.status,
            'remaining_minutes': remaining_minutes,
            'remaining_seconds': remaining_seconds,
        }
        return JsonResponse(data)

    except HallPass.DoesNotExist:
        return JsonResponse({'error': "Hall Pass not found"}, status=404)
    
def user_logout(request):
    logout(request)
    return redirect('passapp-login')