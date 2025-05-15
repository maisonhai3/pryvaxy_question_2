import os
from datetime import datetime

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.exceptions import InfluxDBError
from fastapi import HTTPException

# InfluxDB connection parameters
INFLUXDB_URL = os.environ.get("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN", "my-super-secret-token")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG", "my-org")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET", "time-series-data")


DEFAULT_MEASUREMENT = "feature_data"


def get_influxdb_client():
    """
    Create and return an InfluxDB client as a dependency.

    This function is used with FastAPI's dependency injection system to provide
    an InfluxDB client to route handlers.
    """
    try:
        client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )

        yield client

    finally:
        client.close()


async def post_point_to_feature_and_customer(
    client: InfluxDBClient, feature_id: str, customer_id: str, data
):
    write_api = client.write_api()

    point = (
        Point(DEFAULT_MEASUREMENT)
        .tag("feature_id", feature_id)
        .tag("customer_id", customer_id)
        .field("value", data.value)
        .time(datetime.utcnow())
    )

    write_api.write(bucket=INFLUXDB_BUCKET, record=point)
    return True


async def get_feature_median_of_feature_and_customer(client, feature_id, customer_id):
    query_api = client.query_api()

    # Approximate or exact? I assume we use approximate to save resources
    query = f"""
    from(bucket: "{INFLUXDB_BUCKET}") \
        |> range(start: -30d) \
        |> filter(fn: (r) => r._measurement == "{DEFAULT_MEASUREMENT}")
        |> filter(fn: (r) => r["feature_id"] == "{feature_id}")
        |> filter(fn: (r) => r["customer_id"] == "{customer_id}")
        |> median()
    """

    result = query_api.query(query=query)

    median = None
    for table in result:
        for record in table.records:
            median = record.get_value()
            break

    return median


async def delete_points_of_feature_customer_before(
    client, feature_id, customer_id, before
):
    delete_api = client.delete_api()

    delete_api.delete(
        start="1970-01-01T00:00:00Z",  # The origin of everything :D
        stop=before,
        predicate=f"_measurement={DEFAULT_MEASUREMENT} AND feature_id={feature_id} AND customer_id={customer_id}",
        bucket=INFLUXDB_BUCKET,
        org=INFLUXDB_ORG,
    )

    return True


async def get_midrange_of_feature_and_customer(
    client, feature_id, customer_id, interval="1h"
):
    query_api = client.query_api()

    query = f"""
    from(bucket: "{INFLUXDB_BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r._measurement == "{DEFAULT_MEASUREMENT}")
        |> filter(fn: (r) => r["feature_id"] == "{feature_id}")
        |> filter(fn: (r) => r["customer_id"] == "{customer_id}")
        |> aggregateWindow(every: {interval}, fn: mean, createEmpty: false)
        |> yield(name: "mean")
    """

    result = query_api.query(query=query)

    values = []
    for table in result:
        for record in table.records:
            values.append(record.get_value())

    if len(values) == 0:
        return None

    min_val = min(values)
    max_val = max(values)
    midrange = (max_val - min_val) / 2

    return {"min": min_val, "max": max_val, "midrange": midrange}
