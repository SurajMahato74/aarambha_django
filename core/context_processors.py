from .models import OurWork

def our_work_items(request):
    return {
        'our_work_items': OurWork.objects.filter(is_active=True)  # or your custom method
    }
