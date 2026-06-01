# Generated migration for inventory modules

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0018_remove_attendance_subject_biometriclog_and_more'),
    ]

    operations = [
        # Add new fields to InventoryItem
        migrations.AddField(
            model_name='inventoryitem',
            name='item_type',
            field=models.CharField(
                choices=[('consumable', 'Consumable'), ('fixed', 'Fixed Asset'), ('general', 'General')],
                default='general',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),

        # Create ConsumableItem model
        migrations.CreateModel(
            name='ConsumableItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('category', models.CharField(default='General', max_length=80)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('unit', models.CharField(default='pcs', max_length=20)),
                ('location', models.CharField(blank=True, max_length=120)),
                ('reorder_level', models.PositiveIntegerField(default=5)),
                ('supplier_name', models.CharField(blank=True, max_length=160)),
                ('cost_per_unit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),

        # Create FixedItem model
        migrations.CreateModel(
            name='FixedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=160)),
                ('category', models.CharField(default='General', max_length=80)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('location', models.CharField(blank=True, max_length=120)),
                ('serial_number', models.CharField(blank=True, max_length=100, unique=True)),
                ('purchase_date', models.DateField(blank=True, null=True)),
                ('purchase_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('depreciation_rate', models.DecimalField(decimal_places=2, default=0, help_text='Percentage per year', max_digits=5)),
                ('condition', models.CharField(choices=[('new', 'New'), ('good', 'Good'), ('fair', 'Fair'), ('poor', 'Poor'), ('damaged', 'Damaged')], default='new', max_length=20)),
                ('warranty_expiry', models.DateField(blank=True, null=True)),
                ('last_maintenance_date', models.DateField(blank=True, null=True)),
                ('next_maintenance_date', models.DateField(blank=True, null=True)),
                ('remarks', models.TextField(blank=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]

