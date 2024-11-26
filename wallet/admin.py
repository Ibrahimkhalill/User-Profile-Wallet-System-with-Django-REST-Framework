from django.contrib import admin
from .models import UserProfile, Wallet

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Wallet)