from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_payments(request):
    """Get current user's payments"""
    payments = Payment.objects.filter(user=request.user).order_by('-paid_at')
    
    data = []
    for payment in payments:
        data.append({
            'id': payment.id,
            'amount': str(payment.amount),
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'is_verified': payment.is_verified,
            'paid_at': payment.paid_at.isoformat(),
        })
    
    return Response(data)