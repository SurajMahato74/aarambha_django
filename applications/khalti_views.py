from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
import requests
from django.utils import timezone
from django.conf import settings

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_khalti_payment(request, pk):
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        
        if not application.payment_required:
            return Response({'error': 'Payment not required for this application'}, status=status.HTTP_400_BAD_REQUEST)
        
        if application.payment_completed:
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        khalti_url = 'https://pay.khalti.com/api/v2/epayment/initiate/'
        payload = {
            'return_url': request.build_absolute_uri(f'/payment/success/{pk}/'),
            'website_url': request.build_absolute_uri('/'),
            'amount': int(application.payment_amount * 100),
            'purchase_order_id': f'APP{application.id}',
            'purchase_order_name': f'Membership Fee - {application.full_name}',
            'customer_info': {
                'name': application.full_name,
                'email': application.user.email,
                'phone': application.phone
            },
            'amount_breakdown': [
                {
                    'label': 'Membership Fee',
                    'amount': int(application.payment_amount * 100)
                }
            ],
            'product_details': [
                {
                    'identity': f'APP{application.id}',
                    'name': 'Aarambha Foundation Membership',
                    'total_price': int(application.payment_amount * 100),
                    'quantity': 1,
                    'unit_price': int(application.payment_amount * 100)
                }
            ]
        }
        
        headers = {
            'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(khalti_url, json=payload, headers=headers)
        
        try:
            data = response.json()
        except:
            data = {'error': response.text}
        
        if response.status_code == 200 and 'pidx' in data:
            return Response({
                'pidx': data.get('pidx'),
                'payment_url': data.get('payment_url'),
                'expires_at': data.get('expires_at'),
                'expires_in': data.get('expires_in'),
                'full_response': data  # For debugging
            })
        else:
            return Response({'error': 'Failed to initiate payment', 'details': data, 'status_code': response.status_code}, status=status.HTTP_400_BAD_REQUEST)
    
    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def verify_khalti_payment(request, pk):
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        pidx = request.GET.get('pidx') or request.data.get('pidx')

        if not pidx:
            return Response({'error': 'Payment ID not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Idempotency: If already verified, return success
        if application.payment_completed and application.khalti_payment_token == pidx:
            return Response({
                'message': 'Payment already verified successfully',
                'application': ApplicationSerializer(application).data
            })

        khalti_url = 'https://pay.khalti.com/api/v2/epayment/lookup/'
        payload = {'pidx': pidx}
        headers = {
            'Authorization': f'key {settings.KHALTI_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        response = requests.post(khalti_url, json=payload, headers=headers)
        data = response.json()

        if response.status_code == 200 and data.get('status', '').lower() == 'completed':
            application.payment_completed = True
            application.khalti_transaction_id = data.get('transaction_id')
            application.khalti_payment_token = pidx
            application.payment_date = timezone.now()
            application.save()

            return Response({
                'message': 'Payment verified successfully',
                'application': ApplicationSerializer(application).data
            })
        else:
            return Response({'error': 'Payment verification failed', 'details': data}, status=status.HTTP_400_BAD_REQUEST)

    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
