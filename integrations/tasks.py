from celery import shared_task
import time


@shared_task(bind=True, max_retries=3)
def simulate_external_sync(self, integration_id):
    try:
        print(f"Processing integration {integration_id}")
        time.sleep(5)  # simula chamada externa
        print("Finished processing")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)