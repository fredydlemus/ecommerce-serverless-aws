import os
import json
import logging
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

ORDERS_TABLE = os.environ["ORDERS_TABLE"]

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        order_id     = body.get("orderId")
        customer_id  = body.get("customerId")
        order_date   = body.get("orderDate")
        status       = body.get("status", "PENDING")
        items        = body.get("items")
        total_amount = body.get("totalAmount")

        if not (order_id and customer_id and order_date and isinstance(items, list) and total_amount):
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "Missing or invalid fields"})
            }
        
        table = dynamodb.Table(ORDERS_TABLE)

        table.put_item(Item={
            "orderId":     order_id,
            "customerId":  customer_id,
            "orderDate":   order_date,
            "status":      status,
            "items":       items,
            "totalAmount": total_amount
        })

        return {
            "statusCode": 201,
            "body": json.dumps({
                "orderId": order_id,
                "message": "Order created successfully"
            })
        }
    
    except ClientError as e:
        logger.error("AWS client error: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "AWS error"})
        }
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }