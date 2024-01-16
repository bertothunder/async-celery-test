import os
import sys
import logging
import traceback
from celery import Task


logger = logging.getLogger(f"celery.base_task")


class JobException(Exception):
    pass


def handle_error():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    trace = traceback.extract_tb(exc_traceback)
    # don't want the current frame in the traceback
    if len(trace) > 1:
        trace = trace[1:]
    trace.reverse()
    trace_summary = '/'.join([os.path.splitext(os.path.basename(tr.filename))[0] + '.' + tr.name for tr in trace])
    # tb = [{'line': tr.line, 'file': tr.filename, 'lineno': tr.lineno, 'func': tr.name} for tr in trace]
    error_report = {
        'error_msg': str(exc_value),
        'error_summary': trace_summary,
        'error_class': exc_type.__name__,
        'error_traceback': traceback.format_exc(),
    }
    logger.critical(f"{trace_summary}. {exc_type.__name__} : {exc_value}", extra=error_report)


class BaseTask(Task):
    default_retry_delay = 10
    # hard time limit
    time_limit = 15 * 60 * 1
    # soft time limit
    soft_time_limit = 60 * 10

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        handle_error()
        task_name = '.'.join(self.name.rsplit('.', 2)[-2:])

        extra = {
            'celery_task_id': task_id, "celery_status": "fail",
            "task_name": task_name}
        extra.update(self.__dict__.get('extra', {}))
        logger.critical(f"Task {task_name} failed: {exc}", extra=extra)

    def on_success(self, retval, task_id, args, kwargs):
        task_name = '.'.join(self.name.rsplit('.', 2)[-2:])

        extra = {
            'celery_task_id': task_id, "celery_status": "success",
            "task_name": task_name}
        extra.update(self.__dict__.get('extra', {}))
        logger.info(f"Task {task_name} succeeded", extra=extra)

        logger.info(f"task {task_id} succeeded: {retval}", extra=extra)
