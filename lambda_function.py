import random
from datetime import UTC, datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Packages")


def lambda_handler(event, context):
    try:
        package_id = event["queryStringParameters"]["packageId"]

        # 현재 시간을 ISO 형식으로 저장
        current_time = datetime.now(UTC).isoformat()

        # DynamoDB에서 패키지 조회
        response = table.get_item(Key={"packageId": package_id})

        if "Item" not in response:
            return {"statusCode": 404, "body": "Package not found"}

        valid = True  # 여기서는 임시로 True로 설정했습니다. 실제 비즈니스 로직에 따라 변경 필요

        if valid:
            # 상태를 'readyForTQ'로 업데이트
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
            # 상태를 'receiveUnavailable'로 업데이트
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
