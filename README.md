= NOT FOR PRODUCTION =

This is a test to see how CDK works, published such that all can benefit.

== NOTES ==

The target accounts default VPC setup, needs default subnets for the intended
VPCs subnets. Otherwise the AZ locating mechanic cant find the place to put the
subnets.

Error experienced:

```
AWS::EC2::Subnet SubnetBPrivate Template error: Fn::Select cannot select nonexistent value at index 1
```

