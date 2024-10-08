from django.urls import path
from laptopApproval.views import *

urlpatterns = [
    path('register/', register_user, name = 'register_user'),
    path('login/', login_user, name= 'login_user'),
    path('user/profile/', view_logged_in_user_profile, name='view_logged_in_user_profile'),
    path('users/', view_user_profiles, name='view_user_profiles'),

    path('employees/employee-create/', create_employee),
    path('employees/employee-list/', list_employee),
    path('employees/<int:emp_id>/details/', get_employee_details),
    path('employees/employee-update/', update_employees),
    path('employees/<int:emp_id>/delete/', delete_employees),
    path('employees/employee-deleted-list/', list_deleted_employee),
    path('employees/employee-restore/', restore_employee),

    path('managers/manager-create/', create_manager),
    path('managers/manager-list/', list_managers),
    path('managers/<int:manager_id>/details/', get_manager_details),
    path('managers/manager-update/', update_manager),
    path('managers/<int:manager_id>/delete/', delete_manager),
    path('managers/manager-deleted-list/', list_deleted_managers),
    path('managers/manager-restore/', restore_manager),

    path('laptop-requests/create/', create_laptop_request),
    path('laptop-requests/<int:request_id>/update/', update_laptop_request),
    path('laptop-requests/', view_laptop_request),
    path('laptop-requests/approve-rejection/<int:request_id>/', approve_reject_laptop_request),
    path('laptop-requests/<int:request_id>/delete/', delete_laptop_request),
    path('laptop-requests/stats/', get_laptop_request_stats),


    path('request-approval/history/', view_approval_history),

    path('laptop-inventory/create/', create_laptop_inventory),
    path('laptop-inventory/view-inventory/', view_laptop_inventory),
    path('laptop-inventory/<int:laptop_id>/update/', update_laptop_inventory),
    path('laptop-inventory/<int:laptop_id>/delete/', delete_laptop_inventory),

    path('search/laptop-request/', search_laptop_requests)

]
