import sentry_sdk
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Letting


def index(request):
    """
    Renders the index page displaying a list of all lettings.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered 'lettings/index.html' template with the lettings list.
    """
    try:
        # Lettings.index view logic
        lettings_list = Letting.objects.all()
        context = {'lettings_list': lettings_list}
        return render(request, 'lettings/index.html', context)
    except Exception as e:
        # Capturing sentry exception
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message("Erreur dans lettings.views index.")
        return render(request, '500.html', status=500)


def letting(request, letting_id):
    """
    Renders the detail page for a specific letting.
    Args:
        request (HttpRequest): The HTTP request object.
        letting_id (int): The id of the letting to display.
    Returns:
        HttpResponse: The rendered 'lettings/letting.html' template with the letting's data.
    """
    try:
        # Lettings.letting view logic
        letting = get_object_or_404(Letting, id=letting_id)
        context = {
            'title': letting.title,
            'address': letting.address,
        }
        return render(request, 'lettings/letting.html', context)
    except Http404:
        # Username doesn't exist, 404
        return render(request, '404.html', status=404)
    except Exception as e:
        # Capturing other exception
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message("Erreur dans lettings.views index.")
        return render(request, '500.html', status=500)
