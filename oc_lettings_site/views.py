import sentry_sdk
from django.shortcuts import render


def index(request):
    """
    Renders the main index page.
    Args:
        request: The HTTP request object.
    Returns:
        HttpResponse: The rendered 'index.html' template.
    """
    try:
        return render(request, 'oc_lettings_site/index.html')
    except Exception as e:
        # Capturing sentry exception
        sentry_sdk.capture_exception(e)
        sentry_sdk.capture_message("Erreur dans oc_lettings_site.views index.")
        return render(request, '500.html', status=500)
