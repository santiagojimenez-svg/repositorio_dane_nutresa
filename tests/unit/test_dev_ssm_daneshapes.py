import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
try:
    from moto import mock_ssm
except ImportError:
    from moto import mock_aws as mock_ssm

from src.features.DataMaestraDaneShapes.main import get_aws_account, get_ssm_client, set_shapes_bucket

class Test_Dev_SSM_DaneShapes():
    
    ssm_env_name = '/ml/misc/foundation/env_name'
    ssm_feature_store_bucket_name = '/ml/s3/foundation/feature_store_bucket_name'
    
    aws_account = None
    feature_store_bucket = None
    
    @mock_ssm
    def init(self):
        self.ssm = get_ssm_client()
        self.ssm.put_parameter(
            Name=self.ssm_feature_store_bucket_name,
            Description = "Shapes bucket",
            Value="machine-learning-helados-featurestore-lab",
            Type="String")
        self.ssm.put_parameter(
            Name=self.ssm_env_name,
            Description = "Environment variable",
            Value="hel001",
            Type="String")
        self.aws_account = get_aws_account(self.ssm)
        self.feature_store_bucket = set_shapes_bucket(self.ssm,self.aws_account)