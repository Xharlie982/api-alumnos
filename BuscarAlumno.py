import boto3, json

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
    res = table.get_item(Key={'tenant_id': tenant_id, 'alumno_id': alumno_id})
    item = res.get('Item')

    if not item:
        return {'statusCode': 404, 'error': 'Alumno no encontrado'}

    # Salida
    return {'statusCode': 200, 'alumno': item}
