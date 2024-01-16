# Celery test

This test checks Celery capability using asyncio and SOLO worker, with two or more tasks concurrently
executing async tasks in the celery pool

Celery has to be launched with the `solo` pool, it's ok to add concurrent workers.

`celery --workdir . --app tasks.all worker --loglevel=info --concurrency=3 --pool=solo`
