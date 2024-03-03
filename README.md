# EBS-Cost-Optimization-Cleaner
Lambda function that identifies EBS snapshots no longer associated with any active EC2 instance and deletes them to save on storage costs.

## Lambda Function Working:
The function performs the following actions:

1. **Initialization**: Creates an EC2 client using Boto3, enabling it to make requests to the EC2 service.
2. **Retrieve all EBS snapshots**: Uses the `describe_snapshots` method to fetch all EBS snapshots owned by the account, identified by `OwnerIds=['self']`.
3. **Fetch all running EC2 instance IDs**: Retrieves a list of all currently running EC2 instances using the `describe_instances` method with a filter for `instance-state-name` as 'running'. Collects all instance IDs into a set called `active_instance_ids`.
4. **Loop through each snapshot**: Iterates over each snapshot to determine if it meets criteria for deletion:

    - If a snapshot is not associated with any volume (`VolumeId` is not present), it is deleted using the `delete_snapshot` method. A message is printed indicating the deletion.
    - If a snapshot is associated with a volume, it checks whether this volume is attached to any running instance by calling the `describe_volumes` method with the volume ID. If the volume is not attached to any instance (`Attachments` is empty), the snapshot is deleted.
    - If the `describe_volumes` call throws an exception with the error code 'InvalidVolume.NotFound', indicating the associated volume does not exist (possibly deleted), the snapshot is deleted.

## Purpose

This function aids in cleaning up unnecessary EBS snapshots that are not attached to any volume or whose volumes are not attached to any running instances. It helps manage costs and maintain a tidy AWS environment by removing unneeded snapshots that could otherwise accumulate over time.

# ----------------------------------------------------------------------------------------------

# If you want to gain hands-on experience with the project, here is an explanation of each step.

Let's start,

1. Create an EC2 instance, and we will create snapshots from the volume of the EC2 instance.

2. You can check if there is a volume created for the EC2 instance by going to the EC2 dashboard and clicking on 'Volumes'. There, you will be able to see the volume created for the instance we just created.

Create an EC2 instance, and we will create snapshots from the volume of the EC2 instance.

You can check if there is a volume created for the EC2 instance by going to the EC2 dashboard and clicking on 'Volumes'. There, you will be able to see the volume created for the instance we just created.

 https://rohitexplainstech.hashnode.dev/navigating-aws-cost-optimization-an-in-depth-guide-day-12

