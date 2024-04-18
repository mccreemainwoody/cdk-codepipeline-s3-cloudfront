#!/usr/bin/env python3
import aws_cdk as cdk

from stacks import CodePipelineS3CloudfrontStack


def main() -> None:
    app = cdk.App()

    CodePipelineS3CloudfrontStack(app, "CodePipelineS3CloudFront")

    app.synth()


if __name__ == "__main__":
    main()
