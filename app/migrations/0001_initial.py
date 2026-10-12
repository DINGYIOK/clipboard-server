from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise.fields.base import OnDelete
from tortoise import fields

class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name='BaseModel',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={'table': 'basemodel', 'app': 'models', 'pk_attr': 'id'},
            bases=['Model'],
        ),
        ops.CreateModel(
            name='User',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('username', fields.CharField(unique=True, max_length=64)),
                ('hash_password', fields.CharField(max_length=255)),
                ('totp_secret', fields.CharField(max_length=100)),
                ('role', fields.CharField(default='VIEWER', max_length=20)),
                ('is_active', fields.BooleanField(default=True)),
            ],
            options={'table': 'user', 'app': 'models', 'pk_attr': 'id', 'table_description': '用户表'},
            bases=['BaseModel'],
        ),
        ops.CreateModel(
            name='Device',
            fields=[
                ('id', fields.IntField(generated=True, primary_key=True, unique=True, db_index=True)),
                ('created_at', fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ('updated_at', fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ('user', fields.ForeignKeyField('models.User', source_field='user_id', db_constraint=True, to_field='id', related_name='devices', on_delete=OnDelete.CASCADE)),
                ('device_name', fields.CharField(unique=True, max_length=64)),
                ('is_active', fields.BooleanField(default=True)),
                ('evm', fields.CharField(max_length=100)),
                ('bitcoin', fields.CharField(max_length=100)),
                ('tron', fields.CharField(max_length=100)),
                ('solana', fields.CharField(max_length=100)),
                ('litecoin', fields.CharField(max_length=100)),
                ('dogecoin', fields.CharField(max_length=100)),
                ('sui', fields.CharField(max_length=100)),
            ],
            options={'table': 'device', 'app': 'models', 'pk_attr': 'id', 'table_description': '设备名称表'},
            bases=['BaseModel'],
        ),
    ]
