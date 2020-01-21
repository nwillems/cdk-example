from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elb2,
)

import aws_cdk.aws_secretsmanager as sm


class CdkExampleStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Some error prevented me from creating the subnets properly
        #  Will investigate soon-ish
        vpc = ec2.Vpc(self, "VPC",
            
        )
        sg_default = ec2.SecurityGroup.from_security_group_id(self, "SG", vpc.vpc_default_security_group)

        # Ensure:
        # 1) password is derived from SM ✓
        # 2) placement is in private subnets ✓
        # 3) Slave in other subnet -

        # Defaults:
        #  - master password stored in SM
        #  - default placement in private subnets
        db = rds.DatabaseInstance(
            self, "RDS",
            master_username="master",
            database_name="db1",
            engine_version="8.0.16",
            engine=rds.DatabaseInstanceEngine.MYSQL,
            vpc=vpc,
            port=3306,
            instance_class=ec2.InstanceType.of(
                ec2.InstanceClass.MEMORY4, 
                ec2.InstanceSize.LARGE,
            ),
            security_groups=[sg_default],
            removal_policy=core.RemovalPolicy.DESTROY,
            deletion_protection=False
        )

        default_userdata = ec2.UserData.for_linux()
        db_password = db.secret.secret_value.to_string()
        db_host=db.instance_endpoint.hostname
        default_userdata.add_commands("echo \"username=admin\npassword={}\nhost={}\" > /home/ubuntu/.mysql.creds".format(db_password, db_host))

        asg = autoscaling.AutoScalingGroup(
            self, "ASG",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.GenericLinuxImage({"eu-west-1": "ami-02df9ea15c1778c9c"}),
            desired_capacity=2,
            # Probably ensure we can access the machines...
            associate_public_ip_address=True,
            key_name="nicolai-test",
            user_data=default_userdata,
        )
        # asg.add_security_group(ssh_from_everywhere)

        alb = elb2.ApplicationLoadBalancer(
            self, "ALB",
            vpc=vpc,
            internet_facing=True,
        )
        listener = alb.add_listener(
            "ALBListener", protocol=elb2.ApplicationProtocol.HTTP,
        )
        listener.add_targets("ASGTarget", targets=[asg], port=8080 )
