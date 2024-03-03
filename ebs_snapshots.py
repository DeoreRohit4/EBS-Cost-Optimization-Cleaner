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
