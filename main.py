from fastapi import FastAPI, Depends, Path, HTTPException
from typing import Annotated

from influxdb_client import InfluxDBClient

from database import get_influxdb_client
from database.influx import (
    post_point_to_feature_and_customer,
    get_feature_median_of_feature_and_customer,
)
from models import FeatureData

app = FastAPI(
    title="Time Series API",
    description="API for storing and retrieving time series data",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Time Series API"}


@app.post("/data/features/{feature_id}/customers/{customer_id}")
async def post_feature_data(
    feature_id: Annotated[str, Path(description="Unique identifier for the feature")],
    customer_id: Annotated[str, Path(description="Unique identifier for the customer")],
    data: FeatureData,
    influxdb_client: InfluxDBClient = Depends(get_influxdb_client),
):
    """
    Store feature data for a specific customer in the time series database.
    """

    # Validate if the featureId and customerId exist: SKIPPED

    try:
        result = await post_point_to_feature_and_customer(
            client=influxdb_client,
            feature_id=feature_id,
            customer_id=customer_id,
            data=data,
        )
        if result:
            return {
                "status": "success",
                "message": "Data received",
                "feature_id": feature_id,
                "customer_id": customer_id,
                "data": data,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to write the datapoint to the database.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/data/features/{feature_id}/customers/{customer_id}/median")
async def get_feature_median(
    feature_id: Annotated[str, Path(description="Unique identifier for the feature")],
    customer_id: Annotated[str, Path(description="Unique identifier for the customer")],
    influxdb_client: InfluxDBClient = Depends(get_influxdb_client),
):
    """
    Get the median value for a feature for a specific customer.
    """

    try:
        result = await get_feature_median_of_feature_and_customer(
            client=influxdb_client,
            feature_id=feature_id,
            customer_id=customer_id,
        )
        if result:
            return {
                "status": "success",
                "message": "Median retrieved",
                "feature_id": feature_id,
                "customer_id": customer_id,
                "median": result,
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve the median value from the database.",
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

    # I'll take a short breaktime.
