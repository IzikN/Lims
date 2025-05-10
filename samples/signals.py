from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Sample

def generate_sample_id():
    from datetime import date
    today = date.today()
    prefix = "JGLSP2500"
    count = Sample.objects.count() + 1
    return f"{prefix}-{str(count).zfill(3)}"

@receiver(pre_save, sender=Sample)
def set_sample_id(sender, instance, **kwargs):
    if not instance.sample_id:
        instance.sample_id = generate_sample_id()
