from celery import shared_task
import time

@shared_task(bind=True)
def long_task(self):
    total = 20

    for i in range(total):
        time.sleep(1)

        percent = int((i + 1) / total * 100)

        self.update_state(
            state="PROGRESS",
            meta={"progress": percent}
        )

    return {"progress": 100}