import os
import time
from django.apps import AppConfig
from .startup import run_startup_tasks

class aeconConfig(AppConfig):
    name = 'aecon'
    server_start_time = None

    def ready(self):
            print("AECON ready")
            # Check if main run
            if os.environ.get("DEBUG") == 'True':
                if os.environ.get('RUN_MAIN') == 'true':
                    aeconConfig.server_start_time = time.time()
                    run_startup_tasks(aeconConfig.server_start_time)
                    from .scheduler import start_scheduler
                    start_scheduler()
            else:
                aeconConfig.server_start_time = time.time()
                run_startup_tasks(aeconConfig.server_start_time)
                from .scheduler import start_scheduler
                start_scheduler()
