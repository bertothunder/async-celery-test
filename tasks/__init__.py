import asyncio
import logging
import functools
from celery import Celery

from .base_task import BaseTask


REDIS_TRANSPORT_OPTIONS = dict(
    health_check_interval=5,
    socket_keepalive=True,
    socket_timeout=5,
    retry_on_timeout=True,
)

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('celery.test')
container_name = 'local'


app = Celery(container_name,
             broker=f"redis://localhost:8082/11",
             backend=f"redis://localhost:8082/11",
             task_serializer='msgpack',
             task_cls=BaseTask,
             )

app.conf.update(task_default_queue=container_name,
                task_default_exchange=container_name,
                task_default_routing_key=container_name,
                worker_hijack_root_logger=False,
                task_always_eager=False,
                broker_transport_options=REDIS_TRANSPORT_OPTIONS,
                result_expires=3 * 3600,
                accept_content=['pickle', 'json', 'msgpack'])

DEFAULT_TASK_REDIS_KEY = "default_task"


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        print(*args)
        return asyncio.get_event_loop().run_until_complete(f(*args, **kwargs))
    return wrapper

