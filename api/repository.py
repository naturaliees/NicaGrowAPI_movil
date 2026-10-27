from django.db import connection
from rest_framework.exceptions import NotFound, ValidationError
from .catalog import TABLES

def resolve(schema, table):
    if table not in TABLES.get(schema, []):
        raise NotFound('Tabla no disponible.')
    return '[' + schema + '].[' + table + ']'

def quote(name):
    return '[' + name.replace(']', ']]') + ']'

def metadata(schema, table):
    resolve(schema, table)
    with connection.cursor() as cursor:
        cursor.execute('''SELECT c.COLUMN_NAME, c.DATA_TYPE, c.IS_NULLABLE,
            CASE WHEN p.COLUMN_NAME IS NULL THEN 0 ELSE 1 END AS is_pk
            FROM INFORMATION_SCHEMA.COLUMNS c
            LEFT JOIN (
                SELECT k.TABLE_SCHEMA, k.TABLE_NAME, k.COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE k
                JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
                ON k.CONSTRAINT_CATALOG=t.CONSTRAINT_CATALOG
                AND k.CONSTRAINT_SCHEMA=t.CONSTRAINT_SCHEMA AND k.CONSTRAINT_NAME=t.CONSTRAINT_NAME
                WHERE t.CONSTRAINT_TYPE='PRIMARY KEY'
            ) p ON c.TABLE_SCHEMA=p.TABLE_SCHEMA AND c.TABLE_NAME=p.TABLE_NAME AND c.COLUMN_NAME=p.COLUMN_NAME
            WHERE c.TABLE_SCHEMA=%s AND c.TABLE_NAME=%s ORDER BY c.ORDINAL_POSITION''', [schema, table])
        columns = [{'nombre': r[0], 'tipo': r[1], 'nullable': r[2] == 'YES', 'pk': bool(r[3])} for r in cursor.fetchall()]
    if not columns:
        raise NotFound('La tabla no existe o el usuario SQL no puede ver su estructura.')
    return columns

def select_rows(schema, table, params):
    target = resolve(schema, table)
    columns = metadata(schema, table)
    names = {c['nombre'] for c in columns}
    reserved = {'pagina', 'tamano', 'orden'}
    unknown = set(params) - names - reserved
    if unknown:
        raise ValidationError({'filtros': 'Campos desconocidos: ' + ', '.join(sorted(unknown))})
    try:
        page = int(params.get('pagina', 1)); size = int(params.get('tamano', 100))
    except (ValueError, TypeError):
        raise ValidationError('pagina y tamano deben ser enteros.')
    if not 1 <= page <= 100000 or not 1 <= size <= 500:
        raise ValidationError('pagina: 1..100000; tamano: 1..500.')
    keys = [c['nombre'] for c in columns if c['pk']]
    order = params.get('orden')
    if order and order.lstrip('-') not in names:
        raise ValidationError('Columna de orden desconocida.')

    order_columns = ([order.lstrip('-')] if order else []) + [k for k in keys if not order or k != order.lstrip('-')]
    ordering = ', '.join(quote(k) + (' DESC' if order and order.startswith('-') and k == order[1:] else ' ASC') for k in order_columns) or '(SELECT NULL)'
    filters = [(k, v) for k, v in params.items() if k in names]
    where = ' WHERE ' + ' AND '.join(quote(k) + ' = %s' for k, v in filters) if filters else ''
    values = [v for k, v in filters]
    # Column/table identifiers come only from the allowlist and SQL metadata.
    with connection.cursor() as cursor:
        cursor.execute('SELECT COUNT_BIG(*) FROM ' + target + where, values)
        total = cursor.fetchone()[0]
        cursor.execute('SELECT ' + ', '.join(quote(c['nombre']) for c in columns) + ' FROM ' + target + where + ' ORDER BY ' + ordering + ' OFFSET %s ROWS FETCH NEXT %s ROWS ONLY', values + [(page - 1) * size, size])
        data = [dict(zip([c['nombre'] for c in columns], row)) for row in cursor.fetchall()]
    return {'pagina': page, 'tamano': size, 'total': total, 'paginacion_estable': bool(keys), 'advertencia': None if keys else 'Sin clave primaria: el orden entre páginas no está garantizado. Consulta estructura para revisar las columnas.', 'datos': data}

