from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Job, CandidateProfile, JobApplication
from .utility import extract_text_from_pdf, calculate_match_score
from .forms import ResumeUploadForm
from .gemini_ai import analyze_resume_with_gemini
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('upload_resume')  
    else:
        form = UserCreationForm()
    return render(request, 'jobs/signup.html', {'form': form})




def job_list(request):
    query = request.GET.get('q', '')
    jobs = Job.objects.all().order_by('-created_at')
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(company__icontains=query)
    return render(request, 'jobs/job_list.html', {'jobs': jobs, 'query': query})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    if request.user.is_authenticated:
        has_applied = JobApplication.objects.filter(job=job, candidate=request.user).exists()
    return render(request, 'jobs/job_detail.html', {'job': job, 'has_applied': has_applied})

@login_required
def job_create(request):
    if request.method == 'POST':
        Job.objects.create(
            title=request.POST.get('title'),
            company=request.POST.get('company'),
            description=request.POST.get('description'),
            requirements=request.POST.get('requirements'),
            location=request.POST.get('location'),
            posted_by=request.user
        )
        return redirect('job_list')
    return render(request, 'jobs/job_form.html')

@login_required
def upload_resume(request):
    try:
        profile, created = CandidateProfile.objects.get_or_create(user=request.user)
        ai_feedback = None
        
        if request.method == 'POST':
            form = ResumeUploadForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                
                if 'resume_file' in request.FILES:
                    profile.resume_file = request.FILES['resume_file']
                    profile.save()
                    
                    try:
                        file_path = profile.resume_file.path
                        profile.extracted_text = extract_text_from_pdf(file_path)
                    except Exception as e:
                        profile.extracted_text = f"Error reading PDF file: {str(e)}"
                    
                    profile.save()

                if profile.extracted_text and not profile.extracted_text.startswith("Error"):
                    sample_job_desc = "Looking for a Python Django developer with experience in scikit-learn, databases, and web deployment."
                    try:
                        ai_feedback = analyze_resume_with_gemini(profile.extracted_text, sample_job_desc)
                    except Exception as e:
                        ai_feedback = f"AI Evaluation unavailable: {str(e)}"
                    
                return redirect('upload_resume')
        else:
            form = ResumeUploadForm(instance=profile)
            if profile.extracted_text:
                sample_job_desc = "Looking for a Python Django developer with experience in scikit-learn, databases, and web deployment."
                try:
                    ai_feedback = analyze_resume_with_gemini(profile.extracted_text, sample_job_desc)
                except Exception:
                    pass

        return render(request, 'jobs/upload_resume.html', {
            'form': form, 
            'profile': profile, 
            'ai_feedback': ai_feedback
        })
    except Exception as e:
        # Fallback rendering to prevent 500 error page if anything else fails
        return render(request, 'jobs/upload_resume.html', {
            'form': ResumeUploadForm(),
            'profile': None,
            'ai_feedback': f"An error occurred loading your profile: {str(e)}"
        })
        
@login_required
def apply_to_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    profile = CandidateProfile.objects.filter(user=request.user).first()
    if not profile or not profile.resume_file:
        return redirect('upload_resume')
    
    score = calculate_match_score(job.description + " " + job.requirements, profile.extracted_text)
    
    JobApplication.objects.get_or_create(
        job=job,
        candidate=request.user,
        defaults={'match_score': score}
    )
    return redirect('my_applications')

@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(candidate=request.user).order_by('-applied_at')
    try:
        profile = request.user.candidate_profile
    except CandidateProfile.DoesNotExist:
        profile = None
    return render(request, 'jobs/my_applications.html', {'applications': applications, 'profile': profile})

# Create your views here.
