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

```python
 import boto3

 def lambda_handler(event, context):
     ec2 = boto3.client('ec2')

     # Retrieve all EBS snapshots
     response = ec2.describe_snapshots(OwnerIds=['self'])

     # Fetch all running EC2 instance IDs
     instances_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
     active_instance_ids = set()

     for reservation in instances_response['Reservations']:
         for instance in reservation['Instances']:
             active_instance_ids.add(instance['InstanceId'])

     # Loop through each snapshot and delete if not attached to any volume or if the volume is not attached to a running instance
     for snapshot in response['Snapshots']:
         snapshot_id = snapshot['SnapshotId']
         volume_id = snapshot.get('VolumeId')

         if not volume_id:
             # If the snapshot is not attached to any volume, delete it
             ec2.delete_snapshot(SnapshotId=snapshot_id)
             print(f"Deleted EBS snapshot {snapshot_id} because it was not attached to any volume.")
         else:
             # Verify if the volume exists
             try:
                 volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                 if not volume_response['Volumes'][0]['Attachments']:
                     ec2.delete_snapshot(SnapshotId=snapshot_id)
                     print(f"Deleted EBS snapshot {snapshot_id} because it originated from a volume not attached to any running instance.")
             except ec2.exceptions.ClientError as e:
                 if e.response['Error']['Code'] == 'InvalidVolume.NotFound':
                     # If the volume associated with the snapshot does not exist (might have been deleted)
                     ec2.delete_snapshot(SnapshotId=snapshot_id)
                     print(f"Deleted EBS snapshot {snapshot_id} because its associated volume was not found.")
```

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/a807dd3e-bf24-4b7a-8d9c-ad52a54349be)

Click on "Deploy" and then click on "Test" to trigger the function.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/bfd06b3f-db9d-4a34-b0f2-94d2beb33d8f)

When you hit the 'Test' button, a window to configure the test event will pop up. Just give the event a name and save it.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/1b792d9c-8b83-4933-8dd4-f05018681c93)

Click on 'Test' again to trigger the function.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/3f9a59f4-bb42-443e-ad0b-19e2f3988eb9)

Error will occur that "Task timed out after 3.03 seconds"

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/d5c9847d-614a-4a60-b395-0609fb26f643)

Go to the Configuration tab and edit the Timeout setting to 10 seconds.
In General Congiguration Click on Edit.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/8061a7f6-4887-4b6d-8337-b6e16b8f5e78)

Set to 10 seconds and Save

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/873d8b72-52e0-4a31-8eb5-4609af7a1124)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/09890829-f1e4-4c5e-bc70-9879240154fa)

6. Hit "Test" button again to trigger function and you will see an error.
The error message indicates that the IAM role cost-optimization-function-role-10vh6cs1 used by your AWS Lambda function (or any other service assuming this role) does not have the necessary permissions to perform the ec2:DescribeSnapshots action. To resolve this issue, you need to attach a policy granting the ec2:DescribeSnapshots permission to the role.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/2b7f2fd1-c59e-415a-82af-772a5dd8c6d2)

Now, go to IAM and click on "Policies".

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/703f3d7f-f83b-4aba-bb26-59065ef34b32)

Click on 'Create Policy'

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/272e5225-214a-47ca-a6a7-e36d1a036349)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/13c9617e-325f-4e14-aa2a-860b4d2e2a72)

Select the EC2 service, search for snapshots, and choose 'DescribeSnapshots'.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/9dda9f4e-c211-4cac-a937-be27a5d28c8b)

Also, search for 'DeleteSnapshot' and select it, as we need this for the deletion of a snapshot. Then, in resources, select 'All' if not selected by default.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/1e6c3a92-a710-4fc9-ada1-a12bc5e1336c)

Click the "Next" button.
Then enter a name for the policy.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/7f15a600-0e49-4ecf-ad7f-80303ba7de62)

Click the "Create policy" button.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/a9133f37-ab35-4f16-9d7e-29cc7f1ca29b)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/3455938b-dda5-4df8-90d8-b9434bf49e98)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/27f2c22e-3266-4dc4-a8ba-cc9002d66b60)

You can see that the policy has been created.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/bfb4bc93-1ed8-4fe5-901f-166904d07a97)

Now, return to the Lambda function and navigate to the "Configuration" tab. Select "Permissions," and then, under "Execution role," locate "Role name." Below it, you will find a link. Simply click on that link.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/bf08775d-9314-46d5-b6d1-cf3ae59b16b1)

Here, go to 'Add permissions'.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/c17807fe-a86e-4413-b7c9-46a178121a06)

Select "Attach policies"

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/45174bda-8902-4b7a-95c4-736271f45e78)

Then search for the policy you just created, select it, and then click the 'Add permissions' button.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/3f14ce2b-7a1c-4127-a23a-13e898231f32)

Now, go ahead and click the "Test" button in the Lambda function. You will see an error stating, "When calling the DescribeInstances operation: You are not authorized to perform this operation." To resolve this, you need to grant the necessary permissions by creating a new policy.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/82fc4655-44f0-4e0a-ba7c-6808fdaab8a5)

Navigate to policies and create one for DescribeInstances and DescribeVolumes.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/909d576b-d774-4f6d-bb90-4b537a600632)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/7bfe7123-7edd-4415-924a-c67190e490a1)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/7cc08dc1-aa9a-4d7a-bf52-727185ea2bfa)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/7c2340e3-e1e8-414b-8ad2-011a4e7a9e1b)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/626f3c04-9e6d-4026-bfe1-1c4416291c52)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/a0a30e15-aaee-49e7-943e-77cbca101538)

Now, go back to the Lambda function and enter the Configuration tab. Select Permissions, then click the link below 'Role name'.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/a71fd57d-5fa9-4307-9118-da42eb191169)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/5d25f29d-5d88-40fe-89ad-7a046ec56267)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/8a154a87-0992-45fd-9ea8-f5e9aa16d3d2)

Policy was successfully attached to role.
Now, go back to the Lambda function and trigger it using the "Test" button.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/021e3cc9-0dd5-4699-bce6-a0118d3d01e0)

You can see that it executed successfully and found nothing to delete.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/f274def9-807f-4add-84da-33dcf1811d49)

Please go and check if that snapshot has been deleted. You will find that it has not been deleted because the EC2 instance is still running.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/62572a1a-a8db-4dd6-bc14-cadae64dac33)

7. Now, go ahead and terminate the EC2 instance. After doing so, check for the snapshot; it will still be present. Terminating an EC2 instance only deletes that instance and the volume attached to it.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/e2aa6599-9eff-4222-8641-59a3654b760d)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/f5847ef8-254a-44dc-bae5-fb93da6c0844)

Snapshot is not deleted.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/ea251f65-6e64-4389-9913-cb4804575db7)

Now, go and trigger the Lambda function by clicking the 'Test' button.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/fa765050-8eca-4edd-a643-f44b044dc9d8)

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/7fac13a7-13bb-4e6c-9aca-414697395291)

See the function logs it indicates that, "Deleted EBS snapshot snap-0aa45e3267e46ee83 because its associated volume was not found."
Go and check for snapshots; you will see that there are no snapshots.

![image](https://github.com/DeoreRohit4/EBS-Cost-Optimization-Cleaner/assets/102886808/624c267c-2b0d-4941-89c7-259071c887dc)

The project is completed.
You can create hundreds of snapshots, and they will all be deleted in one go if they are not associated with a volume.

## THANK YOU!
