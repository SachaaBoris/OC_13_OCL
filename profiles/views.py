import sentry_sdk
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Profile


def index(request):
    """
    Renders the index page displaying a list of all user profiles.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered 'profiles/index.html' template with the profiles list.
    """
    try:
        # Profiles.index view logic
        profiles_list = Profile.objects.all()
        context = {'profiles_list': profiles_list}
        return render(request, 'profiles/index.html', context)
    except Exception as e:
        # Capturing sentry exception
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message("Erreur dans profiles.views index.")
        return render(request, '500.html', status=500)


def profile(request, username):
    """
    Renders the detail page for a specific user profile.
    Args:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the user whose profile is to be displayed.
    Returns:
        HttpResponse: The rendered 'profiles/profile.html' template with the user's profile data.
    """
    try:
        # Profiles.profile view logic
        profile = get_object_or_404(Profile, user__username=username)
        context = {'profile': profile}
        return render(request, 'profiles/profile.html', context)
    except Http404:
        # Username doesn't exist, 404
        return render(request, '404.html', status=404)
    except Exception as e:
        # Capturing other exception
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message("Erreur dans profiles.views profile.")
        return render(request, '500.html', status=500)
