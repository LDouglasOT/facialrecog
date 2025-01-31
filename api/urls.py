from django.urls import path
from .views import train_face, recognize_face
from .views import *
from .child import *
from .clearence import *
from .notifications import *
from .Parent import *
from .auth import *
from .Pledge import *
from .attendances import *

urlpatterns = [
    path('train/', train_face, name='train_face'),
    path('recognize/', recognize_face, name='recognize_face'),
    path('create-attendance/', create_attendance, name='create_attendance'),
    path('get-attendance/', get_attendance_by_id, name='get_attendance'),
    path('update-attendance/', update_attendance, name='update_attendance'),
    path('delete-attendance/', delete_attendance, name='delete_attendance'),
    
    # Authentication URLs
    path('otp/', generate, name='generate_otp'),
    path('verify/', verify, name='verify'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('generatenum/', generate_phone_number, name='generate_phone_number'),
    path('paynow/', pay_now, name='pay_now'),
    
    # Child URLs
    path('create-child/', create_child, name='create_child'),
    path('get-children/', get_child_by_id, name='get_children'),
    path('update-child/', update_child, name='update_child'),
    path('delete-child/', delete_child, name='delete_child'),
    
    # Clearance Code URLs
    path('create-clearance/', create_clearance_code, name='create_clearance_code'),
    path('get-clearances/', get_all_clearance_codes, name='get_all_clearance_codes'),
    path('single-clearance/', get_clearance_code, name='get_clearance_code'),
    path('update-clearance/', update_clearance_code, name='update_clearance_code'),
    path('check-clearance/', check_clearance, name='check_clearance'),
    path('quick-login/', quick_login, name='quick_login'),
    
    # Notifications URLs
    path('get-notifications/', get_all_notifications, name='get_notifications'),
    
    # Parent URLs
    path('create-parent/', create_parent, name='create_parent'),
    path('check-visitations/', check_visitations, name='check_visitations'),
    
    # Pledge URLs
    path('create-pledge/', create_pledge, name='create_pledge'),
    path('check-pledge/', check_pledge, name='check_pledge'),
]
