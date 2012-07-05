class Command(BaseCommand):

    def handle(self, *args, **options):
        r = csv.reader(open(args[0]))
        headers = r.next()
        data = {}
        for row in r:
            datum = dict(zip(headers, row))
            print datum
