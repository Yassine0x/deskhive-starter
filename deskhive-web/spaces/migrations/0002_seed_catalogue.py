from django.db import migrations

CATALOGUE = {'lyo': {'city': 'Lyon', 'address': '10 rue de la République, Lyon', 'spaces': [{'name': 'Lyon Open Desk', 'kind': 'desk', 'capacity': 1, 'hourly_rate': '12.00'}, {'name': 'Lyon Meeting Room', 'kind': 'meeting_room', 'capacity': 6, 'hourly_rate': '30.00'}]}, 'lil': {'city': 'Lille', 'address': '20 rue Nationale, Lille', 'spaces': [{'name': 'Lille Open Desk', 'kind': 'desk', 'capacity': 1, 'hourly_rate': '10.00'}, {'name': 'Lille Meeting Room', 'kind': 'meeting_room', 'capacity': 8, 'hourly_rate': '25.00'}]}, 'bcn': {'city': 'Barcelona', 'address': '30 carrer de Balmes, Barcelona', 'spaces': [{'name': 'Barcelona Open Desk', 'kind': 'desk', 'capacity': 1, 'hourly_rate': '15.00'}, {'name': 'Barcelona Meeting Room', 'kind': 'meeting_room', 'capacity': 10, 'hourly_rate': '40.00'}]}}

def seed(apps, schema_editor):
    Location = apps.get_model('spaces', 'Location')
    Space = apps.get_model('spaces', 'Space')
    alias = schema_editor.connection.alias
    for code, values in CATALOGUE.items():
        location = Location.objects.using(alias).create(code=code, city=values['city'], address=values['address'])
        for item in values['spaces']:
            suffix = 'desk' if item['kind'] == 'desk' else 'room'
            Space.objects.using(alias).create(code=f'{code}-{suffix}', location=location, **item)

class Migration(migrations.Migration):
    dependencies = [('spaces', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
