from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Role, TechnicianProfile

@receiver(post_save, sender=User)
def handle_user_profile_creation(sender, instance, created, **kwargs):
    """
    Ensure TechnicianProfile exists if user has TECHNICIAN role.
    """
    if instance.role == Role.TECHNICIAN:
        TechnicianProfile.objects.get_or_create(user=instance)
