from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.views.generic import CreateView,UpdateView
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView,PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import EmployerCreationForm,EmployerUpdateForm,DynamicForm
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth.mixins import LoginRequiredMixin


class UserCreateView(CreateView):
    form_class = EmployerCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, "Registration Successful!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Registration Failed!")
        return super().form_invalid(form)

class UserEditView( UpdateView):
    model = User 
    form_class = EmployerUpdateForm
    template_name = 'edit_profile.html'
    success_url = reverse_lazy('employer')

    def get_object(self, queryset=None):
        
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Profile updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update profile. Please try again.")
        return super().form_invalid(form)
    
class UserLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        messages.success(self.request, "Login Successful!")
        return reverse_lazy('employer')  

    def form_invalid(self, form):
        messages.error(self.request, "Invalid login credentials!")
        return super().form_invalid(form)
    
class UserChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'change_password.html'
    success_url = reverse_lazy('employer')  

    def form_valid(self, form):  
        form.save()
        messages.success(self.request, "Your password was changed successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to change password. Please ensure the information is correct.")
        return super().form_invalid(form)


def user_logout(request):
    logout(request)  
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')
    
@login_required
def employer_dashboard(request):
    return render(request, 'employer.html', {
        'user': request.user
    })


@csrf_exempt
def form_builder(request):
    if request.method == 'GET':
        session_key = request.session.session_key or request.session.create()
        fields = FormField.objects.filter(form__isnull=True, session_key=session_key)
        forms = Form.objects.all()
        return render(request, 'form_builder.html', {'fields': fields, 'forms': forms})
    elif request.method == 'POST':
        data = json.loads(request.body)
        session_key = request.session.session_key or request.session.create()
        field = FormField.objects.create(
            label=data['label'],
            field_type=data['field_type'],
            order=FormField.objects.filter(form__isnull=True, session_key=session_key).count(),
            session_key=session_key
        )
        return JsonResponse({'id': field.id, 'label': field.label, 'field_type': field.field_type})

@csrf_exempt
def save_form(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form_name = data.get('name')
        if not form_name:
            return JsonResponse({'status': 'error', 'message': 'Form name is required'}, status=400)

        session_key = request.session.session_key or request.session.create()
        form = Form.objects.create(name=form_name)
        FormField.objects.filter(form__isnull=True, session_key=session_key).update(form=form, session_key=None)
        return JsonResponse({'status': 'success', 'form_id': form.id})

@csrf_exempt
def reorder_fields(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        for index, field_id in enumerate(data['order']):
            FormField.objects.filter(id=field_id).update(order=index)
        return JsonResponse({'status': 'success'})

@csrf_exempt
def submit_form(request, form_id):
    if request.method == 'POST':
        try:
            form = Form.objects.get(id=form_id)
            submitted_data = json.loads(request.body)
            FormSubmission.objects.create(form=form, submitted_data=submitted_data)
            return JsonResponse({'status': 'success', 'message': 'Form submitted successfully.'})
        except Form.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Form not found.'}, status=404)

def view_form(request, form_id):
    form = Form.objects.get(id=form_id)
    fields = form.fields.all()
    return render(request, 'view_form.html', {'form': form, 'fields': fields})

def view_submissions(request, form_id):
    form = Form.objects.get(id=form_id)
    submissions = form.submissions.all()
    return render(request, 'formdatalist.html', {'form': form, 'submissions': submissions})


def delete_submission(request, form_id, submission_id):
    if request.method == 'POST':
        form = get_object_or_404(Form, id=form_id)
        submission = get_object_or_404(form.submissions, id=submission_id)
        submission.delete()
        messages.success(request, "Submission deleted successfully.")
    return redirect('view_submissions', form_id=form_id)

@csrf_exempt
def edit_submission(request, form_id, submission_id):
    try:
        
        form = Form.objects.get(id=form_id)
        submission = FormSubmission.objects.get(id=submission_id, form=form)

        fields = form.fields.all()
        submitted_data = submission.submitted_data

        if request.method == 'GET':
            form_instance = DynamicForm(fields=fields, initial=submitted_data)
            return render(request, 'edit_submission.html', {'form': form_instance, 'form_id': form.id, 'submission_id': submission.id})

        elif request.method == 'POST':
            data = json.loads(request.body)
            form_instance = DynamicForm(data=data, fields=fields)

            if form_instance.is_valid():
                submission.submitted_data = form_instance.cleaned_data
                submission.save()
                return JsonResponse({'status': 'success', 'message': 'Submission updated successfully.'})
            else:
                return JsonResponse({'status': 'error', 'errors': form_instance.errors}, status=400)

    except Form.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Form not found.'}, status=404)
    except FormSubmission.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Submission not found.'}, status=404)
