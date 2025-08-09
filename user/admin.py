from django.contrib import admin
from .models import CustomUser
from django.utils.html import format_html

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active', 'is_staff', 'profile_picture')
    list_filter = ('user_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('user_type',)

    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'phone_no', 'terms_agree', 'remember_me')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('User Type', {
            'fields': ('user_type',)
        }),
    )
    def profile_picture(self, obj):
       if hasattr(obj, 'profile') and obj.profile.image:
           return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />', obj.profile.image.url)
       return "No Image"
    profile_picture.short_description = 'Profile Pic'

admin.site.register(CustomUser, CustomUserAdmin)

