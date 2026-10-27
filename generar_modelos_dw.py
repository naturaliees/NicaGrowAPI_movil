"""Generate explicit unmanaged DW models from SQL Server metadata (read-only SQL)."""
import os
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection
from api.catalog import TABLES
base = Path(__file__).parent / 'api'
models = ['"""Existing NicaGrow_DW dimensions and facts; Django does not manage DDL."""', 'from django.db import models', '']
serializers = ['from rest_framework import serializers', 'from . import models', '']
resources = []
for table in TABLES['dw']:
    class_name = table.replace('_', '')
    with connection.cursor() as cursor:
        cursor.execute('''SELECT c.name, ty.name, c.max_length, c.precision, c.scale, c.is_nullable, c.is_identity,
            CASE WHEN pk.column_id IS NULL THEN 0 ELSE 1 END,
            rt.name, rc.name
            FROM sys.tables t JOIN sys.schemas s ON s.schema_id=t.schema_id
            JOIN sys.columns c ON c.object_id=t.object_id JOIN sys.types ty ON ty.user_type_id=c.user_type_id
            LEFT JOIN (SELECT ic.object_id,ic.column_id FROM sys.index_columns ic
                       JOIN sys.indexes i ON i.object_id=ic.object_id AND i.index_id=ic.index_id WHERE i.is_primary_key=1) pk
              ON pk.object_id=c.object_id AND pk.column_id=c.column_id
            LEFT JOIN sys.foreign_key_columns fk ON fk.parent_object_id=c.object_id AND fk.parent_column_id=c.column_id
            LEFT JOIN sys.tables rt ON rt.object_id=fk.referenced_object_id
            LEFT JOIN sys.columns rc ON rc.object_id=fk.referenced_object_id AND rc.column_id=fk.referenced_column_id
            WHERE s.name=%s AND t.name=%s ORDER BY c.column_id''', ['dw', table])
        columns = cursor.fetchall()
    if not columns:
        raise RuntimeError('Missing DW table: ' + table)
    models.append(f'class {class_name}(models.Model):')
    names = []
    for name, typ, length, precision, scale, nullable, identity, primary, ref, ref_col in columns:
        names.append(name)
        options = [f'db_column={name!r}']
        if primary: options.append('primary_key=True')
        if nullable: options.extend(['null=True', 'blank=True'])
        if ref:
            if ref not in TABLES['dw']: raise RuntimeError('Reference outside DW allowlist')
            field = f'models.ForeignKey({ref.replace("_", "")!r}, on_delete=models.DO_NOTHING, ' + ', '.join(options) + ')'
        else:
            if identity: field_type = 'BigAutoField' if typ == 'bigint' else 'AutoField'
            elif typ in ('varchar', 'char', 'nvarchar', 'nchar'):
                field_type = 'CharField'; options.append(f'max_length={length // 2 if typ.startswith("n") else length}')
            elif typ == 'date': field_type = 'DateField'
            elif typ in ('datetime', 'datetime2'): field_type = 'DateTimeField'
            elif typ == 'decimal':
                field_type = 'DecimalField'; options.extend([f'max_digits={precision}', f'decimal_places={scale}'])
            elif typ in ('int', 'bigint'): field_type = 'BigIntegerField' if typ == 'bigint' else 'IntegerField'
            else: raise RuntimeError(f'Unsupported SQL type {typ}')
            field = f'models.{field_type}(' + ', '.join(options) + ')'
        models.append(f'    {name} = {field}')
    models.extend(['', '    class Meta:', '        managed = False', f'        db_table = "[dw].[{table}]"', ''])
    serializers.extend([f'class {class_name}Serializer(serializers.ModelSerializer):', '    class Meta:', f'        model = models.{class_name}', f'        fields = {names!r}', '        read_only_fields = fields', ''])
(base / 'models.py').write_text('\n'.join(models), encoding='utf-8')
(base / 'serializers.py').write_text('\n'.join(serializers), encoding='utf-8')
print(f'Generated {len(TABLES["dw"])} DW models and serializers. No staging tables queried.')
