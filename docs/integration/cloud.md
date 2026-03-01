## ☁️ Cloud Services Integration

### **AWS Integration**

```python
# aws_integration.py - AWS services integration
import boto3
import asyncio
from botocore.config import Config
from typing import Dict, List, Optional
import json

class AWSIntegration:
    """Integration with AWS services for cloud-native Codomyrmex deployment."""

    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.config = Config(
            region_name=region,
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )

        # Initialize clients
        self.s3 = boto3.client('s3', config=self.config)
        self.lambda_client = boto3.client('lambda', config=self.config)
        self.sqs = boto3.client('sqs', config=self.config)
        self.sns = boto3.client('sns', config=self.config)
        self.cloudwatch = boto3.client('cloudwatch', config=self.config)

    async def store_analysis_artifacts(self, analysis_id: str,
                                     artifacts: Dict[str, bytes],
                                     bucket_name: str) -> List[str]:
        """Store analysis artifacts in S3."""
        stored_keys = []

        for artifact_name, artifact_data in artifacts.items():
            key = f"analysis-artifacts/{analysis_id}/{artifact_name}"

            # Upload to S3
            self.s3.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=artifact_data,
                ContentType=self._get_content_type(artifact_name),
                Metadata={
                    'analysis_id': analysis_id,
                    'uploaded_by': 'codomyrmex',
                    'timestamp': str(time.time())
                }
            )

            stored_keys.append(key)
            logger.info(f"Stored artifact {artifact_name} at s3://{bucket_name}/{key}")

        return stored_keys

    async def trigger_lambda_analysis(self, function_name: str,
                                    payload: Dict) -> Dict:
        """Trigger serverless analysis via AWS Lambda."""
        response = self.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )

        # Parse response
        result = json.loads(response['Payload'].read())

        if response['StatusCode'] == 200:
            logger.info(f"Lambda function {function_name} executed successfully")
            return result
        else:
            logger.error(f"Lambda function failed: {result}")
            raise Exception(f"Lambda execution failed: {result}")

    async def send_analysis_notification(self, topic_arn: str,
                                       analysis_result: Dict) -> str:
        """Send analysis completion notification via SNS."""
        message = {
            'analysis_id': analysis_result.get('id'),
            'status': analysis_result.get('status'),
            'completion_time': analysis_result.get('completion_time'),
            'summary': analysis_result.get('summary', {})
        }

        response = self.sns.publish(
            TopicArn=topic_arn,
            Subject='Codomyrmex Analysis Complete',
            Message=json.dumps(message, indent=2),
            MessageAttributes={
                'analysis_type': {
                    'DataType': 'String',
                    'StringValue': analysis_result.get('type', 'unknown')
                }
            }
        )

        return response['MessageId']

    async def publish_custom_metrics(self, metrics: List[Dict]):
        """Publish custom CloudWatch metrics."""
        metric_data = []

        for metric in metrics:
            metric_data.append({
                'MetricName': metric['name'],
                'Value': metric['value'],
                'Unit': metric.get('unit', 'Count'),
                'Dimensions': [
                    {
                        'Name': dim_name,
                        'Value': dim_value
                    }
                    for dim_name, dim_value in metric.get('dimensions', {}).items()
                ]
            })

        # Publish metrics (CloudWatch accepts up to 20 metrics per call)
        for i in range(0, len(metric_data), 20):
            batch = metric_data[i:i+20]

            self.cloudwatch.put_metric_data(
                Namespace='Codomyrmex',
                MetricData=batch
            )

        logger.info(f"Published {len(metric_data)} custom metrics")

    def _get_content_type(self, filename: str) -> str:
        """Get content type based on file extension."""
        content_types = {
            '.json': 'application/json',
            '.txt': 'text/plain',
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.html': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.pdf': 'application/pdf'
        }

        extension = Path(filename).suffix.lower()
        return content_types.get(extension, 'application/octet-stream')

# Usage example for cloud-native analysis workflow
async def cloud_analysis_workflow(codebase_path: str, aws_integration: AWSIntegration):
    """Complete cloud-native analysis workflow."""
    from codomyrmex.coding.static_analysis import analyze_codebase
    from codomyrmex.data_visualization import create_analysis_dashboard

    analysis_id = f"analysis_{int(time.time())}"

    try:
        # 1. Perform static analysis
        analysis_result = analyze_codebase(codebase_path)

        # 2. Generate visualization artifacts
        dashboard_data = create_analysis_dashboard(analysis_result)

        # 3. Store artifacts in S3
        artifacts = {
            'analysis_report.json': json.dumps(analysis_result, indent=2).encode(),
            'dashboard.html': dashboard_data['html'].encode(),
            'metrics.json': json.dumps(dashboard_data['metrics'], indent=2).encode()
        }

        stored_keys = await aws_integration.store_analysis_artifacts(
            analysis_id, artifacts, 'codomyrmex-analysis-bucket'
        )

        # 4. Trigger additional Lambda processing if needed
        lambda_result = await aws_integration.trigger_lambda_analysis(
            'codomyrmex-post-process',
            {
                'analysis_id': analysis_id,
                'artifact_keys': stored_keys,
                'analysis_summary': analysis_result.get('summary', {})
            }
        )

        # 5. Publish metrics
        await aws_integration.publish_custom_metrics([
            {
                'name': 'AnalysisCompleted',
                'value': 1,
                'dimensions': {'analysis_type': 'static_analysis'}
            },
            {
                'name': 'FilesAnalyzed',
                'value': len(analysis_result.get('files', [])),
                'unit': 'Count'
            },
            {
                'name': 'IssuesFound',
                'value': len(analysis_result.get('issues', [])),
                'unit': 'Count'
            }
        ])

        # 6. Send notification
        notification_id = await aws_integration.send_analysis_notification(
            'arn:aws:sns:us-east-1:123456789:codomyrmex-notifications',
            {
                'id': analysis_id,
                'status': 'completed',
                'completion_time': datetime.utcnow().isoformat(),
                'summary': analysis_result.get('summary', {}),
                'artifacts': stored_keys
            }
        )

        logger.info(f"Cloud analysis workflow completed: {analysis_id}")
        return {
            'analysis_id': analysis_id,
            'artifacts': stored_keys,
            'lambda_result': lambda_result,
            'notification_id': notification_id
        }

    except Exception as e:
        logger.error(f"Cloud analysis workflow failed: {e}")

        # Send error notification
        await aws_integration.send_analysis_notification(
            'arn:aws:sns:us-east-1:123456789:codomyrmex-alerts',
            {
                'id': analysis_id,
                'status': 'failed',
                'error': str(e),
                'completion_time': datetime.utcnow().isoformat()
            }
        )

        raise
```

