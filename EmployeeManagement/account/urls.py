from django.urls import path
from account import views

urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('edit-profile',views.UserEditView.as_view(),name='edit_profile'),
    path('change_password/', views.UserChangePasswordView.as_view(), name='change_password'),
    path('', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('employer/', views.employer_dashboard, name='employer'),
    path('form_builder/', views.form_builder, name='form_builder'),
    path('reorder_fields/', views.reorder_fields, name='reorder_fields'),
    path('save_form/', views.save_form, name='save_form'),
    path('submit_form/<int:form_id>/', views.submit_form, name='submit_form'),
    path('view_form/<int:form_id>/', views.view_form, name='view_form'),
    path('view_submissions/<int:form_id>/', views.view_submissions, name='view_submissions'),
    path('form/<int:form_id>/submission/<int:submission_id>/delete/', views.delete_submission, name='delete_submission'),
    path('edit_submission/<int:form_id>/<int:submission_id>/', views.edit_submission, name='edit_submission'),
]
