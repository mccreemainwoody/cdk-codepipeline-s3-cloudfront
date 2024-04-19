import aws_cdk as core
import aws_cdk.assertions as assertions
import aws_cdk.aws_s3 as s3
import pytest

from cdk_codepipeline_s3_cloudfront.stacks import (
    CodePipelineS3CloudfrontStack
)


@pytest.fixture
def stack() -> CodePipelineS3CloudfrontStack:
    return CodePipelineS3CloudfrontStack(
        core.App(),
        "CodePipelineS3CloudFront"
    )


@pytest.fixture
def template(stack) -> assertions.Template:
    return assertions.Template.from_stack(stack)


@pytest.fixture
def bucket(stack) -> s3.Bucket:
    return stack.node.find_child("StaticWebsiteBucket")


def test_s3_bucket_is_configured_as_static_website(template, bucket):
    assert bucket.is_website


def test_has_cloudfront_distribution_linked_to_bucket(stack, template, bucket):
    template.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": {
                "Origins": [
                    {
                        "DomainName": stack.resolve(
                            bucket.bucket_regional_domain_name
                        )
                    }
                ]
            }
        }
    )


def test_cloudfront_distribution_redirects_to_https(template):
    template.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": {
                "ViewerCertificate": {
                    "CloudFrontDefaultCertificate": True
                }
            }
        }
    )


def test_has_codepipeline(template, stack, bucket):
    template.has_resource_properties(
        "AWS::CodePipeline::Pipeline",
        {
            "Stages": [
                {
                    "Name": "Source",
                    "Actions": [
                        {
                            "Name": "GitHub_Source",
                            "ActionTypeId": {
                                "Category": "Source",
                                "Owner": "ThirdParty",
                                "Provider": "GitHub",
                                "Version": "1"
                            }
                        }
                    ]
                },
                {
                    "Name": "Deploy",
                    "Actions": [
                        {
                            "Name": "S3_Deploy",
                            "ActionTypeId": {
                                "Category": "Deploy",
                                "Owner": "AWS",
                                "Provider": "S3",
                                "Version": "1"
                            },
                            "Configuration": {
                                "BucketName": stack.resolve(bucket.bucket_name)
                            }
                        }
                    ]
                }
            ]
        }
    )
