from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.
User = get_user_model()

class HallPass(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Ended', 'Ended'),
        ('Expired', 'Expired'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passes_as_student',
        verbose_name='Student',
        default=None,
    )
    staff = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='passes_from_staff',
        verbose_name='Staff',
        default=None,
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Active',
    )
    building_from = models.CharField(max_length=30)
    room_from = models.CharField(max_length=30)
    building_to = models.CharField(max_length=30)
    room_to = models.CharField(max_length=30)
    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField(default=5)

    class Meta:
        verbose_name = 'Hall Pass'
        verbose_name_plural = 'Hall Passes'

    def __str__(self):
        return f"{self.student.get_full_name()} to {self.room_to} authorized by {self.staff.get_full_name()}"