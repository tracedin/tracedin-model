import random
import time
import uuid
import pandas as pd

def generate_sample_data(num_samples=10, anomaly_ratio=0.05, max_spans_per_transaction=100):
    data = []

    service_names = ["auth-service", "payment-service", "order-service", "user-service"]
    project_keys = ["proj-123", "proj-456", "proj-789", "proj-000"]
    span_names = ["GET /api/auth", "POST /api/pay", "GET /api/order", "GET /api/user"]

    response_codes = ["200", "201", "404", "500", "403"]
    messages = ["OK", "Created", "Not Found", "Internal Server Error", "Forbidden"]

    current_time = int(time.time() * 1000)

    for i in range(num_samples):
        num_spans = random.randint(20, max_spans_per_transaction)
        trace_id = str(uuid.uuid4())

        service_name = random.choice(service_names)
        project_key = random.choice(project_keys)

        spans = []

        for _ in range(num_spans):
            span_id = str(uuid.uuid4())
            parent_span_id = str(uuid.uuid4())
            span_name = random.choice(span_names)

            response_code = random.choice(response_codes)
            message = random.choice(messages)

            normal_duration = random.randint(100, 2000)
            anomaly_duration = random.randint(3000, 10000)

            if random.random() < anomaly_ratio:
                duration = anomaly_duration
            else:
                duration = normal_duration

            start_time = current_time + random.randint(0, 10000)
            end_time = start_time + duration

            span = {
                "id": span_id,
                "traceId": trace_id,
                "parentSpanId": parent_span_id,
                "name": span_name,
                "serviceName": service_name,
                "projectKey": project_key,
                "kind": "CLIENT",
                "spanType": "HTTP",
                "startEpochMillis": start_time,
                "endEpochMillis": end_time,
                "duration": duration,
                "startDateTime": pd.to_datetime(start_time, unit='ms').isoformat(),
                "data": {
                    "additionalProp1": {},
                    "additionalProp2": {},
                    "additionalProp3": {}
                },
                "capacity": random.randint(0, 1000),
                "totalAddedValues": random.randint(0, 500)
            }

            spans.append(span)

        transaction = {
            "path": f"/api/{service_name}/action",
            "responseCode": response_code,
            "message": message,
            "result": {
                "spans": spans,
                "children": [str(uuid.uuid4())]
            },
            "timeStamp": pd.to_datetime(end_time, unit='ms').isoformat()
        }

        data.append(transaction)

    df = pd.json_normalize(data, record_path=['result', 'spans'], meta=['path', 'responseCode', 'message', 'timeStamp'])
    return df
