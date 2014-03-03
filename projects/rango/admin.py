from django.contrib import admin
from rango.models import Category, Page
from rango.models import UserProfile

class PageAdmin(admin.ModelAdmin):
	list_display = ('title', 'category', 'url', 'views')

# Register your models here.
admin.site.register(Category)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
