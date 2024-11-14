from enum import Enum

from pydantic import BaseModel


class ResourceType(str, Enum):
    AWS_CNR = "aws_cnr"
    GCP_CNR = "gcp_cnr"
    AZURE_CNR = "azure_cnr"


class Config(BaseModel):
    bucket_name: str
    access_key_id: str
    secret_access_key: str

class CreateDatasource(BaseModel):
    name: str
    type: ResourceType
    access_key_id: str
    secret_access_key: str
    use_edp_discount: bool
    linked: bool
    cur_version: Config
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "AWS HQ",
                    "type": "aws_cnr",
                    "config": {
                        "bucket_name": "opt_bucket",
                        "access_key_id": "key_id",
                        "secret_access_key": "secret"
                    },
                    "auto_import": True,
                    "process_recommendations": True
                }
            ]
        }
    }


class DatasourceResponse(BaseModel):
    name: str
    type: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "AWS HQ",
                    "type": "aws_cnr",
                    "config": {
                        "bucket_name": "opt_bucket",
                        "access_key_id": "key_id",
                        "secret_access_key": "secret"
                    },
                    "auto_import": True,
                    "process_recommendations": True
                }
            ]
        }
    }
