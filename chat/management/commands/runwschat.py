from django.core.management import BaseCommand

from tornado import ioloop

from ...apps import tornado_app


class Command(BaseCommand):
    def handle(self, *args, **options):
        tornado_app.listen(8001)
        ioloop.IOLoop.instance().start()
