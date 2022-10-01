from django.contrib import admin
from .models import CriminalMasterData, UserProfile

admin.site.register(UserProfile)
admin.site.register(CriminalMasterData)
# Register your models here.
