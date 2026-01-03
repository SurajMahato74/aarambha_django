#!/usr/bin/env python
"""
Script to update existing approved member applications with payment requirements
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aarambha_foundation.settings')
django.setup()

from applications.models import Application

def update_member_payments():
    # Get all member applications that don't have payment_required set
    member_apps = Application.objects.filter(
        application_type='member',
        payment_required=False
    )
    
    print(f"Found {member_apps.count()} member applications to update")
    
    for app in member_apps:
        app.payment_required = True
        app.payment_amount = 1000  # Fixed price of 1000 NPR
        app.save()
        print(f"Updated application {app.id} for {app.full_name} (Status: {app.status})")
    
    print("Update completed!")

if __name__ == '__main__':
    update_member_payments()