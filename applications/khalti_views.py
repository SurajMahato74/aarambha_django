from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
import requests
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_khalti_payment(request, pk):
    try:
        application = Application.objects.get(pk=pk, user=request.user)
        
        if not application.payment_required:
            return Response({'error': 'Payment not required for this application'}, status=status.HTTP_400_BAD_REQUEST)
        
        if application.payment_completed:
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        khalti_url = 'https://a.khalti.com/api/v2/epayment/initiate/'
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
            'Authorization': 'Key live_secret_key_eace64b3629048ee9467e07b9e950482',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(khalti_url, json=payload, headers=headers)
        
        try:
            data = response.json()
        except:
            data = {'error': response.text}
        
        if response.status_code == 200 and 'payment_url' in data:
            return Response({
                'payment_url': data.get('payment_url'),
                'pidx': data.get('pidx')
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
        
        khalti_url = 'https://a.khalti.com/api/v2/epayment/lookup/'
        payload = {'pidx': pidx}
        headers = {
            'Authorization': 'Key live_secret_key_eace64b3629048ee9467e07b9e950482',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(khalti_url, json=payload, headers=headers)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'Completed':
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
