from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Child)
admin.site.register(Parent)
admin.site.register(Attendance)
admin.site.register(Form)
admin.site.register(Notification)
admin.site.register(ClearanceCode)
admin.site.register(Pledge)
admin.site.register(Transaction)
admin.site.register(Staff)
admin.site.register(Face)
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Order)