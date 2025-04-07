# 필요한 라이브러리 임포트
import random
from datetime import UTC, datetime

import boto3
from boto3.dynamodb.conditions import Key

# DynamoDB 리소스 및 테이블 초기화
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("Packages")


def lambda_handler(event, context):
    """
    AWS Lambda 핸들러 함수: 패키지 상태를 업데이트하는 API 엔드포인트

    Args:
        event (dict): API Gateway에서 전달된 이벤트 데이터
        context (object): Lambda 실행 컨텍스트

    Returns:
        dict: API Gateway 응답 객체 (상태 코드 및 메시지 포함)
    """
    # CORS 헤더 설정
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "3600",
    }

    try:
        # 쿼리 파라미터에서 패키지 ID 추출
        package_id = event["queryStringParameters"]["packageId"]

        # 현재 시간 ISO 형식으로 가져오기
        current_time = datetime.now(UTC).isoformat()

        # DynamoDB에서 패키지 정보 조회
        response = table.get_item(Key={"packageId": package_id})

        # 패키지가 존재하지 않는 경우 404 반환
        if "Item" not in response:
            return {
                "statusCode": 404,
                "headers": cors_headers,
                "body": "Package not found",
            }

        # 패키지 유효성 검사 (현재는 항상 True)
        valid = True

        if valid:
            # 패키지가 유효한 경우: 상태를 'readyForTQ'로 업데이트
            table.update_item(
                Key={"packageId": package_id},
                UpdateExpression="SET #status = :status, receiveDate = :receiveDate",
                ExpressionAttributeNames={"#status": "status"},
                ExpressionAttributeValues={
                    ":status": "readyForTQ",
                    ":receiveDate": current_time,
                },
            )
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": "Package status updated to readyForTQ",
            }
        else:
            # 패키지가 유효하지 않은 경우: 상태를 'receiveUnavailable'로 업데이트
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
                "headers": cors_headers,
                "body": "Package status updated to receiveUnavailable",
            }

    except Exception as e:
        # 오류 발생 시 500 에러 반환
        return {"statusCode": 500, "headers": cors_headers, "body": f"Error: {str(e)}"}
