from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('auth/login/', views.auth_login, name='auth-login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth-refresh'),
    path('auth/logout/', views.auth_logout, name='auth-logout'),
    path('auth/me/', views.auth_me, name='auth-me'),
    path('auth/change-password/', views.auth_change_password, name='auth-change-password'),
    path('profile/', views.profile_detail, name='profile-detail'),
    path('skills/', views.skills_list, name='skills-list'),
    path('skills/<int:pk>/', views.skill_detail, name='skill-detail'),
    path('experience/', views.experiences_list, name='experiences-list'),
    path('experience/<int:pk>/', views.experience_detail, name='experience-detail'),
    path('education/', views.education_list, name='education-list'),
    path('education/<int:pk>/', views.education_detail, name='education-detail'),
    path('categories/', views.categories_list, name='categories-list'),
    path('projects/', views.projects_list, name='projects-list'),
    path('projects/<slug:slug>/', views.project_detail, name='project-detail'),
    path('posts/', views.posts_list, name='posts-list'),
    path('posts/<slug:slug>/', views.post_detail, name='post-detail'),
    path('posts/<slug:slug>/like/', views.post_like, name='post-like'),
    path('comments/', views.comments_list, name='comments-list'),
    path('contact/', views.contact_create, name='contact-create'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('admin/messages/', views.contact_list, name='admin-contact-list'),
]
