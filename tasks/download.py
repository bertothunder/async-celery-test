import httpx
import logging

from tasks import app, sync


logger = logging.getLogger('celery.test.downloader')


@app.task(soft_time_limit=10, ignore_results=True, serializer="pickle")
@sync
async def do_download():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get('https://microsoftedge.github.io/Demos/json-dummy-data/5MB.json')
            logger.info(f"Response detected: {resp.status_code}, length: {len(resp.text)}")
            with open('large-file.json', 'wb') as f:
                f.write(resp.content)
    except Exception as e:
        logger.error(f"Something happened {e}")
