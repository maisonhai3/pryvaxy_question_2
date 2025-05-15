from pydantic import BaseModel, Field


class FeatureData(BaseModel):
    """
    Model for feature data points to be stored in the time series database.
    """

    value: float = Field(..., description="The value of the feature measurement")

    class Config:
        schema_extra = {
            "example": {
                "value": 42.5,
            }
        }
