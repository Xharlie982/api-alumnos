import boto3, json
from boto3.dynamodb.conditions import Attr

def lambda_handler(event, context):
    print(event)
    # Entrada (json)
    body_raw = event.get('body') or {}
    body = json.loads(body_raw) if isinstance(body_raw, str) else body_raw
    tenant_id = body.get('tenant_id')
    alumno_id = body.get('alumno_id')
    if not tenant_id or not alumno_id:
        return {'statusCode': 400, 'error': 'Faltan tenant_id o alumno_id'}

    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')
    try:
        table.delete_item(
            Key={'tenant_id': tenant_id, 'alumno_id': alumno_id},
            ConditionExpression=Attr('tenant_id').exists() & Attr('alumno_id').exists()
        )
        return {'statusCode': 200, 'deleted': True}
    except table.meta.client.exceptions.ConditionalCheckFailedException:
        return {'statusCode': 404, 'error': 'Alumno no existe'}
    except Exception as e:
        return {'statusCode': 500, 'error': 'No se pudo eliminar', 'detail': str(e)}