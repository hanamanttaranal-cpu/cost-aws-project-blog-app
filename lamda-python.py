import boto3

ec2 = boto3.client('ec2', region_name='ap-south-1')
sns = boto3.client('sns', region_name='ap-south-1')

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:542119827827:cost-optimization-alerts"

def lambda_handler(event, context):

    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:AutoStop',
                'Values': ['true']
            },
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )

    instances = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])

    if instances:
        ec2.stop_instances(InstanceIds=instances)

        message = f"Stopped EC2 Instances:\n\n" + "\n".join(instances)

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="AWS Cost Optimization",
            Message=message
        )

        return {
            "statusCode": 200,
            "body": f"Stopped instances: {instances}"
        }

    return {
        "statusCode": 200,
        "body": "No running EC2 instances found with AutoStop=true"
    }
