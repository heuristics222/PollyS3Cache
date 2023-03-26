import os
from aws_cdk import App

from cdk.PollyStack import PollyStack

app = App()
PollyStack(app, "PollyStack",
    env={
        'account': os.environ['CDK_DEFAULT_ACCOUNT'],
        'region': os.environ['CDK_DEFAULT_REGION']
    }
)

app.synth()
