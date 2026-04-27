from .models import StudentProfile

def user_profile(request):
    if request.user.is_authenticated:
        profile = StudentProfile.objects.filter(user=request.user).first()
        return {'profile': profile}
    return {}