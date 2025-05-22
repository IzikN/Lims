from django.contrib import admin
from .models import Sample
from .models import AnalystProfile, TestAssignment

admin.site.register(AnalystProfile)
admin.site.register(TestAssignment)
admin.site.register(Sample)
