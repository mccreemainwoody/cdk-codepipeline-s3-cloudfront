from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    SecretValue
)
from constructs import Construct

from ..DeploymentSettings import DeploymentSettings


CODEPIPELINE_GITHUB_REPO_OWNER = DeploymentSettings.GITHUB_REPO_OWNER
CODEPIPELINE_GITHUB_REPO_NAME = DeploymentSettings.GITHUB_REPO_NAME
CODEPIPELINE_GITHUB_REPO_BRANCH = DeploymentSettings.GITHUB_REPO_BRANCH

SECRETS_MANAGER_GITHUB_TOKEN_KEY = (
    DeploymentSettings.SECRETS_MANAGER_GITHUB_TOKEN_KEY
)


class CodePipelineS3CloudfrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket Setup
        bucket = s3.Bucket(
            self,
            "StaticWebsiteBucket",
            website_index_document="index.html",
            website_error_document="error.html",
            cors=[
                s3.CorsRule(
                    allowed_methods=[
                        s3.HttpMethods.GET
                    ],
                    allowed_origins=[
                        "*"
                    ],
                    allowed_headers=[
                        "*"
                    ]
                )
            ],
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS,
            access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
            versioned=True
        )

        bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                actions=[
                    "s3:GetObject"
                ],
                resources=[
                    bucket.arn_for_objects("*.html"),
                    bucket.arn_for_objects("*.css"),
                    bucket.arn_for_objects("*.js"),
                    bucket.arn_for_objects("*.png"),
                    bucket.arn_for_objects("*.jpg")
                ],
                principals=[
                    iam.AnyPrincipal()
                ]
            )
        )

        # CloudFront Distribution Setup
        distribution = cloudfront.CloudFrontWebDistribution(
            self,
            "CloudFrontDistribution",
            origin_configs=[
                cloudfront.SourceConfiguration(
                    s3_origin_source=cloudfront.S3OriginConfig(
                        s3_bucket_source=bucket
                    ),
                    behaviors=[
                        cloudfront.Behavior(
                            is_default_behavior=True
                        )
                    ]
                )
            ]
        )

        # CodePipeline Pipeline Setup
        pipeline = codepipeline.Pipeline(
            self,
            "DeploymentPipeline"
        )

        # Source Stage Setup
        source_output = codepipeline.Artifact()

        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            output=source_output,
            oauth_token=SecretValue.secrets_manager(
                SECRETS_MANAGER_GITHUB_TOKEN_KEY
            ),
            owner=CODEPIPELINE_GITHUB_REPO_OWNER,
            repo=CODEPIPELINE_GITHUB_REPO_NAME,
            branch=CODEPIPELINE_GITHUB_REPO_BRANCH,
            trigger=codepipeline_actions.GitHubTrigger.WEBHOOK
        )

        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        # Deploy Stage Setup
        deploy_action = codepipeline_actions.S3DeployAction(
            action_name="S3_Deploy",
            input=source_output,
            bucket=bucket,
            extract=True
        )

        pipeline.add_stage(
            stage_name="Deploy",
            actions=[deploy_action]
        )
