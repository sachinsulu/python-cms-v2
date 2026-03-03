import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.db.models import FileField


@receiver(post_delete, sender='media.MediaAsset')
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding MediaAsset is deleted."""
    for field in instance._meta.fields:
        if isinstance(field, FileField):
            file = getattr(instance, field.name, None)
            if file and hasattr(file, 'path') and os.path.isfile(file.path):
                try:
                    os.remove(file.path)
                except Exception:
                    pass


@receiver(pre_save, sender='media.MediaAsset')
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes old file from filesystem when MediaAsset file is replaced."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    for field in instance._meta.fields:
        if isinstance(field, FileField):
            old_file = getattr(old_instance, field.name, None)
            new_file = getattr(instance, field.name, None)
            if old_file and old_file != new_file:
                if hasattr(old_file, 'path') and os.path.isfile(old_file.path):
                    try:
                        os.remove(old_file.path)
                    except Exception:
                        pass
