from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name="login"),
    path('student-home/', views.student_home, name="student_home"),
    path('teacher-home/', views.teacher_home, name="teacher_home"),
    path('admin-home/', views.admin_home, name="admin_home"),
    path('create-task/', views.create_task, name='create_task'),
    path("submit-task/<int:task_id>/", views.submit_task, name="submit_task"),
    path("logout/", views.logout_view, name="logout"),
]


#nujaib-nuju12345(teacher)
#abhinand-abhi123456789(student)
#anjali-kochi12345(teacher)
#avinash-kollam12345(student)