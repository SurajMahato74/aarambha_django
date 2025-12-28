import os
import django
import time
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aarambha_foundation.settings')
django.setup()

from tasks.email_utils import process_email_queue

def run_email_processor():
    print("Email processor started...")
    while True:
        try:
            process_email_queue()
            time.sleep(10)  # Check every 10 seconds
        except KeyboardInterrupt:
            print("Email processor stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)  # Wait longer on error

if __name__ == "__main__":
    run_email_processor()