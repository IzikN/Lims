from django.contrib import admin
from .models import Sample, TestRequest, Attachment

admin.site.register(Sample)
admin.site.register(TestRequest)
admin.site.register(Attachment)
