import boto3, json
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timezone

def lambda_handler(event, context):
    print(event)
    # Entrada (json)
    body_raw = event.get('body') or {}
    body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    tenant_id = body.get('tenant_id')
    alumno_id = body.get('alumno_id')
    alumno_datos = body.get('alumno_datos')  # reemplazo completo (opcional)
    patch = body.get('patch') or {}          # actualización parcial dentro de alumno_datos (opcional)

    if not tenant_id or not alumno_id or (alumno_datos is None and not patch):
        return {'statusCode': 400, 'error': 'Faltan tenant_id/alumno_id o alumno_datos/patch'}

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')

    try:
        if alumno_datos is not None:
            # Reemplaza todo "alumno_datos"
            res = table.update_item(
                Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
                UpdateExpression="SET alumno_datos = :a, actualizado_en = :ts",
                ExpressionAttributeValues={
                    ':a': alumno_datos,
                    ':ts': datetime.now(timezone.utc).isoformat()
                },
                ConditionExpression=Attr('tenant_id').exists() & Attr('alumno_id').exists(),
                ReturnValues="ALL_NEW"
            )
        else:
            # Aplica parches dentro de alumno_datos.campo
            expr_names = {'#ad': 'alumno_datos', '#ts': 'actualizado_en'}
            expr_vals = {':ts': datetime.now(timezone.utc).isoformat()}
            sets = []
            i = 0
            for k, v in patch.items():
                i += 1
                nk = f'#k{i}'
                nv = f':v{i}'
                expr_names[nk] = k
                expr_vals[nv] = v
                sets.append(f"#ad.{nk} = {nv}")

            update_expr = "SET " + ", ".join(sets + ["#ts = :ts"])

            res = table.update_item(
                Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_vals,
                ConditionExpression=Attr('tenant_id').exists() & Attr('alumno_id').exists(),
                ReturnValues="ALL_NEW"
            )

        return {'statusCode': 200, 'updated': res.get('Attributes', {})}
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 404, 'error': 'Alumno no existe'}
    except Exception as e:
        return {'statusCode': 500, 'error': 'No se pudo modificar', 'detail': str(e)}