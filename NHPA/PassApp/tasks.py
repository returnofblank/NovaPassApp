from celery import shared_task
from PassApp.models import HallPass

@shared_task
def expire_hall_pass(pass_id):
    hall_pass = HallPass.objects.get(id=pass_id)
    if hall_pass.status == 'Active':
        hall_pass.status = 'Expired'
        hall_pass.save()