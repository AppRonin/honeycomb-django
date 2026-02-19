import time
from celery import shared_task
from django.core.files.storage import default_storage

from .utils.gpon import (
    get_total_onu,
    get_onu_list,
    get_onu_conf,
    build_template
)

@shared_task(bind=True)
def gpon_conversor_task(self, file_path, port):
    template = None

    try:
        # Get file content
        with default_storage.open(file_path, "r") as f:
            file = f.read()

        self.update_state(state="PROGRESS", meta={"progress": 20})

        # Get total of onu interfaces
        total_onu = get_total_onu(file)
        self.update_state(state="PROGRESS", meta={"progress": 40})
        time.sleep(2)

        # Build a list of new onu interfaces
        # Ex: [1/1/1:1 ... 1/1/1:10]
        onu_list = get_onu_list(total_onu, port)
        self.update_state(state="PROGRESS", meta={"progress": 60})

        # Build an dict with each onu interface and his conf
        onu_conf = get_onu_conf(file, onu_list)
        self.update_state(state="PROGRESS", meta={"progress": 80})

        # Build the template
        template = build_template(onu_conf)
        self.update_state(state="PROGRESS", meta={"progress": 100})
    except Exception as err:
        self.update_state(state="FAILURE", meta={"error": str(err)})
        raise
    finally:
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

    return {"progress": 100, "template": template}