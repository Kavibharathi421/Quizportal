from celery import Celery, Task
from src import create_app
flask_app=create_app()
class FlaskTask(Task):
    def __call__(self,*args,**kwargs):
        with flask_app.app_context():return self.run(*args,**kwargs)
celery=Celery(flask_app.import_name,task_cls=FlaskTask,broker=flask_app.config["CELERY_BROKER_URL"],backend=flask_app.config["CELERY_RESULT_BACKEND"])
celery.conf.update(task_serializer="json",accept_content=["json"],result_serializer="json",task_acks_late=True,worker_prefetch_multiplier=1,task_soft_time_limit=300,task_time_limit=360)
