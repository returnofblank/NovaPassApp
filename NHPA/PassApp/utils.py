from django.utils import timezone
from .locations import locations

def is_valid_location(building, room):
    return building in locations and room in locations[building]

def hall_pass_to_dict(hall_pass):
    return {
        'id': hall_pass.id,
        'student_name': hall_pass.student.get_full_name(),
        'staff_name': hall_pass.staff.get_full_name(),
        'status': hall_pass.status,
        'building_from': hall_pass.building_from,
        'room_from': hall_pass.room_from,
        'building_to': hall_pass.building_to,
        'room_to': hall_pass.room_to,
        'start_time': hall_pass.start_time,
        'duration': hall_pass.duration,
    }

def is_staff_or_admin(user):
    return user.groups.filter(name__in=['staff', 'admin']).exists()

def is_student_member(user):
    return user.groups.filter(name='student').exists()

def matches_nonce(username):
    current_month = timezone.now().strftime('%m')
    return (username[-2:] == current_month) and (username[:2] != '06')
    
def no_nonce(username):
    if username[:2] != '06':
        return username[:-2]
    else:
        return username