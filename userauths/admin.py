from django.contrib import admin
from userauths.models import User,ContactUs,Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.

class User_details(BaseUserAdmin):
    list_display = ('username', 'email', 'dob', 'is_staff')
    search_fields = ['username','email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('dob',)}), # Add your custom field 'dob' to the end
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('dob',)}),
    )

class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name','email','subject']
    
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name','bio','phone']
    
admin.site.register(User,User_details)
admin.site.register(ContactUs,ContactUsAdmin)
admin.site.register(Profile,ProfileAdmin)