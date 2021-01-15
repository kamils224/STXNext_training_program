from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User, dispatch_uid="create_info")
def user_created_info(sender, instance, created, **kwargs):
    print(f"A new user has been created!")



