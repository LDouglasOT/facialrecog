from django.urls import path

from .pay import process_school_payment
from .views import train_face, recognize_face
from .views import *
from .child import *
from .clearence import *
from .notifications import *
from .Parent import *
from .auth import *
from .Pledge import *
from .attendances import *
from .stats import *
from .views import *
from .Orders import *


urlpatterns = [

    #Dashboard URLs
    path('get-stats/', get_stats, name='get_stats'),
    path('get-faces/', getFaces, name='get_faces'),
    #Dashboard URLs end here
    path('get-parents-with-active-pledge/', get_parents_with_active_pledge, name='get_parents_with_active_pledge'),
    path('get-attendances/', get_all_attendances, name='get_attendances'),
    path('form/',getForms.as_view(),name="forms"),

    path('train/', train_face, name='train_face'),
    path('recognize/', recognize_face, name='recognize_face'),
    path('create-attendance/', create_attendance, name='create_attendance'),
    path('get-attendance/', get_attendance_by_id, name='get_attendance'),
    path('update-attendance/', update_attendance, name='update_attendance'),
    path('delete-attendance/', delete_attendance, name='delete_attendance'),
    path("login/", login_view, name="login"),
    # Authentication URLs
    path('otp/', generate, name='generate_otp'),
    path('verify/', verify, name='verify'),
    path('verify-otp/', verify, name='verify_otp'),
    path('generatenum/', generate_phone_number, name='generate_phone_number'),
    path('paynow/', process_school_payment, name='pay_now'),
    path('shop/',getProducts.as_view(),name="shop"),
    
    # Child URLs
    path('create-child/', create_child, name='create_child'),
    path('children/',getChildren,name="getchildren"),
    path('get-children/', get_child_by_id, name='get_children'),
    path('update-child/', update_child, name='update_child'),
    path('delete-child/', delete_child, name='delete_child'),
    
    # Clearance Code URLs
    path('create-clearance/', create_clearance_code, name='create_clearance_code'),
    path('get-clearances/', get_all_clearance_codes, name='get_all_clearance_codes'),
    path('user-clearences/',user_clearences, name="user_clearences"),
    path('single-clearance/', get_clearance_code, name='get_clearance_code'),
    path('update-clearance/', update_clearance_code, name='update_clearance_code'),
    path('check-clearance/', check_clearance, name='check_clearance'),
    path('quick-login/', quick_login, name='quick_login'),
    
    # Notifications URLs
    path('get-notifications/', get_all_notifications, name='get_notifications'),
    path('create-notification/', create_notification, name='create_notification'),
    # Parent URLs
    path('create-parent/', create_parent, name='create_parent'),
    path('check-visitations/', check_visitations, name='check_visitations'),
    
    # Pledge URLs
    path('create-pledge/', create_pledge, name='create_pledge'),
    path('check-pledge/', check_pledge, name='check_pledge'),
    path('get-pledges/',getpledges.as_view(),name="getpledges"),

     path("orders/<uuid:parent_id>/", UserOrdersView.as_view(), name="user-orders"),
]


