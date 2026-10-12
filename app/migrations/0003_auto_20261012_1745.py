from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields

class Migration(migrations.Migration):
    dependencies = [('models', '0002_auto_20261012_1505')]

    initial = False

    operations = [
        ops.AlterField(
            model_name='User',
            name='hash_password',
            field=fields.CharField(default='', max_length=128),
        ),
    ]
