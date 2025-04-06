import random
from datetime import UTC, datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Packages")


def lambda_handler(event, context):
    try:
        package_id = event["queryStringParameters"]["packageId"]

        current_time = datetime.now(UTC).isoformat()

        response = table.get_item(Key={"packageId": package_id})

        if "Item" not in response:
            return {"statusCode": 404, "body": "Package not found"}

        valid = True

        if valid:
            table.update_item(
                Key={"packageId": package_id},
                UpdateExpression="SET #status = :status, receiveDate = :receiveDate",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "readyForTQ",
                    ":receiveDate": current_time,
                },
            )
            return {"statusCode": 200, "body": "Package status updated to readyForTQ"}
        else:
            table.update_item(
                Key={"packageId": package_id},
                UpdateExpression="SET #status = :status, receiveDate = :receiveDate",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "receiveUnavailable",
                    ":receiveDate": current_time,
                },
            )
            return {
                "statusCode": 400,
                "body": "Package status updated to receiveUnavailable",
            }

    except Exception as e:
        return {"statusCode": 500, "body": f"Error: {str(e)}"}
