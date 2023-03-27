from aws_cdk import Duration, Fn, Stack, LegacyStackSynthesizer
from aws_cdk.aws_cloudfront import BehaviorOptions, CfnDistribution, CfnOriginAccessControl, CfnOriginAccessControlProps, Distribution, EdgeLambda, ErrorResponse, LambdaEdgeEventType, OriginAccessIdentity, ViewerProtocolPolicy
from aws_cdk.aws_cloudfront_origins import HttpOrigin, OriginGroup, S3Origin
from aws_cdk.aws_lambda import Code, Function, FunctionUrlAuthType, Runtime, Version
from aws_cdk.aws_iam import Role, PolicyDocument, ServicePrincipal, PolicyStatement, Effect, ManagedPolicy
from aws_cdk.aws_s3 import BlockPublicAccess, Bucket, LifecycleRule
from constructs import Construct

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class PollyStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id,
            synthesizer=LegacyStackSynthesizer(),
            **kwargs)
        codeLocation = 'lambdas'
        # layerLocation = self.installRequirements(codeLocation)
        self.lambdaCode = Code.from_asset(codeLocation)
        self.lambdaRole = self.createLambdaRole()
        # self.lambdaLayer = lambda_.LayerVersion(self, 'lambdaLayer',
        #     code=lambda_.Code.from_asset(layerLocation),
        #     compatible_runtimes=[
        #         lambda_.Runtime.PYTHON_3_8
        #     ]
        # )

        function = self.createLambda('PollyFunction', "PollyFunction.handler")
        functionUrl = function.add_function_url(auth_type=FunctionUrlAuthType.NONE)

        bucket = Bucket(self, 'polly-bucket',
            bucket_name=f'polly-bucket-{self.region}-{self.account}',
            block_public_access=BlockPublicAccess.BLOCK_ALL,
            lifecycle_rules=[
                LifecycleRule(
                    expiration=Duration.days(30),
                ),
            ],
        )
        bucket.grant_write(function)

        origin = S3Origin(
            bucket,
        )
        distribution = Distribution(self, "PollyDistribution",
            default_behavior=BehaviorOptions(
                origin=OriginGroup(
                    primary_origin=origin,
                    fallback_origin=HttpOrigin(Fn.select(2, Fn.split("/", functionUrl.url))),
                    fallback_status_codes=[403]
                ),
                viewer_protocol_policy=ViewerProtocolPolicy.HTTPS_ONLY
            ),
            # error_responses=[
            #     ErrorResponse(
            #         http_status=403,
            #         response_http_status=403,
            #         response_page_path="/error"
            #     )
            # ],
            # additional_behaviors={
            #     "/error": BehaviorOptions(
            #         origin=,
            #         viewer_protocol_policy=ViewerProtocolPolicy.HTTPS_ONLY,
            #         # edge_lambdas=[
            #         #     EdgeLambda(
            #         #         event_type=LambdaEdgeEventType.ORIGIN_REQUEST,
            #         #         function_version=function.current_version
            #         #     )
            #         # ]
            #     )
            # }
        )
        logger.info(distribution.node)

    def createLambda(self, functionName, handlerName):
        return Function(self, functionName,
            code=self.lambdaCode,
            runtime=Runtime.PYTHON_3_8,
            handler=handlerName,
            role=self.lambdaRole,
            # layers=[self.lambdaLayer],
            timeout=Duration.seconds(10),
            reserved_concurrent_executions=1,
        )

    def createLambdaRole(self):
        return Role(self, 'LambdaPolicy',
            assumed_by=ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'PollyPolicy': PolicyDocument(
                    statements=[
                        PolicyStatement(
                            effect=Effect.ALLOW,
                            actions=[
                                'polly:SynthesizeSpeech'
                            ],
                            resources=[
                                '*'
                            ],
                        ),
                    ],
                ),
            },
            managed_policies=[
                ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole'),
            ],
        )