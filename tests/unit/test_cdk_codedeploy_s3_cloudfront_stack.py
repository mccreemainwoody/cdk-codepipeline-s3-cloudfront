import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_codedeploy_s3_cloudfront.cdk_codedeploy_s3_cloudfront_stack import CdkCodedeployS3CloudfrontStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_codedeploy_s3_cloudfront/cdk_codedeploy_s3_cloudfront_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkCodedeployS3CloudfrontStack(app, "cdk-codedeploy-s3-cloudfront")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
