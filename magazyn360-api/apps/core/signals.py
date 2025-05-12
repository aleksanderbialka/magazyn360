from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_group_on_create(sender, instance: CustomUser, created, **kwargs):
    if created:
        instance.sync_group_with_role()
