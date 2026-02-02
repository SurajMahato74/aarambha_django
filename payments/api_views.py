from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment
from applications.models import Application

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_payments(request):
    """Get current user's payments including application payments"""
    data = []
    
    # Get regular payments
    payments = Payment.objects.filter(user=request.user).order_by('-paid_at')
    for payment in payments:
        data.append({
            'id': payment.id,
            'type': 'payment',
            'amount': str(payment.amount),
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'is_verified': payment.is_verified,
            'paid_at': payment.paid_at.isoformat(),
            'description': 'Payment'
        })
    
    # Get application payments (member fees)
    applications = Application.objects.filter(user=request.user, payment_completed=True).order_by('-payment_date')
    for app in applications:
        data.append({
            'id': f'app_{app.id}',
            'type': 'membership_fee',
            'amount': str(app.payment_amount),
            'payment_method': 'Khalti',
            'transaction_id': app.khalti_transaction_id,
            'is_verified': True,
            'paid_at': app.payment_date.isoformat(),
            'description': f'Membership Fee - {app.application_type.title()} Application'
        })
    
    # Sort by payment date (newest first)
    data.sort(key=lambda x: x['paid_at'], reverse=True)
    
    return Response(data)