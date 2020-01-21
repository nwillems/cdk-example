#!/usr/bin/env python3

from aws_cdk import core

from cdk_example.cdk_example_stack import CdkExampleStack

# Created database Master password: hZvR61ARWNCVW6bPMlxw
# Endpoint: database-1.cabdur5bjcpf.eu-west-1.rds.amazonaws.com

app = core.App()
CdkExampleStack(app, "CdkExampleStack", env=core.Environment(region="eu-west-1"))

app.synth()
