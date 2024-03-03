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

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/508983a6-a183-4dee-89ff-a33e08f9c779)
![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/6c5b1db0-db97-483d-b5af-ec9ed84bdffe)

3. Go to the EC2 dashboard, click on Snapshots, and create the snapshots.
- **What is Snapshots:** In Amazon Web Services (AWS), snapshots are point-in-time copies of Amazon Elastic Block Store (EBS) volumes. These snapshots capture the exact state and data of an EBS volume at the moment the snapshot is initiated. Snapshots are stored in Amazon Simple Storage Service (S3) and are used for backups, to replicate data across regions, or to scale vertically by creating new EBS volumes from snapshots.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/9cbe3d4a-e5c8-498e-9f04-e5184f0098f0)
![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/cf8b7337-8185-4320-823b-1264bddb4ffa)

Now select the volume.Scroll down and click on "Create Snapshot".

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/bda5204a-8c80-4417-a346-172951fdeec9)
![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/bd12fa81-7faf-45e7-b44b-ae519ee26f70)

Snapshot is created.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/d40ce9d8-8fc9-4f19-80ff-88ee485b99f4)

Here, we have created a snapshot, and, for example, a developer wants to delete the EC2 instance, volumes, and snapshots. However, they only delete the EC2 instance and forget about the snapshot. They just terminate the EC2 instance, and although the volume gets deleted, the snapshots remain as they are. In such cases, we can use a Lambda function.

4. Navigate to the Lambda functions and create a function for cost optimization. Click on 'Create function'.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/d79a0891-7607-4c4a-b102-5bbb7dc482b6)

Provide the function name and select the Python runtime.Click on "Create Function"

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/044f764a-b940-4f55-8159-3b33ed4b6a78)
![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/e2559f77-da7a-44ac-b039-b11b123ef549)

5. Copy the code provided below and paste it into the 'Code Source' section in lambda_function.py.


