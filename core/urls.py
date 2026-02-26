from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('discover/', views.discover, name='discover'),
    path("profile/", views.profile_view, name="profile"),
    path('create-activity/', views.create_activity, name='create_activity'),
    path('join/<int:activity_id>/', views.join_activity, name='join_activity'),

    path('send-request/<int:user_id>/', views.send_request, name='send_request'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('reject-request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('remove-connection/<int:user_id>/', views.remove_connection, name='remove_connection'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.about, name='about'),
    path('report/<int:user_id>/', views.report_user, name='report_user'),
    path('leave/<int:activity_id>/', views.leave_activity, name='leave_activity'),

]