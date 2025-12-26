def user_context(request):
    """
    Context processor to ensure user is available in all templates
    """
    return {
        'user': getattr(request, 'user', None)
    }
