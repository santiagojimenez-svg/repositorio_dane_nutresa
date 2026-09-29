"""Genera las alertas de los distintos features de la aplicación"""
import logging
from aws_cdk import core as cdk
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as events_targets
from aws_cdk import aws_sns as sns
from aws_cdk import aws_sns_subscriptions as sns_subscriptions
from mlops_skeleton.artifactory.configuration.constants import ArtifactoryConstants
class GenerateFeaturesAlerts(cdk.Construct):
    '''Create Rule and SNS topic for Sagemaker FeatureGroup failure'''
    def __init__(self,
                 scope: cdk.Construct,
                 identifier: str,
                 daneshapes_features_arn: str,
                 construct_id: str,
                 logger: logging.Logger,
                 notifications_email: list,
                 constants:ArtifactoryConstants,
                 **kwargs):
        super().__init__(scope, identifier, **kwargs)
        self.log = logger or logging.getLogger(__name__)
        self.local_constants = constants.features_dictionary.get(construct_id)
        self.sns_topic_name = (
            f'ause1-ml-sns-features-{self.local_constants.get("entidad")}'\
            f'-{self.local_constants.get("fuente")}-failed-pipelines')
        self.rule_name = (
            f'ause1-ml-ev-features-{self.local_constants.get("entidad")}'\
            f'-{self.local_constants.get("fuente")}-failed')

        self.log.info('Creating SNS topic for features failure notification')

        features_failure_notification = sns.Topic(
            scope=self,
            id=self.sns_topic_name,
            topic_name=self.sns_topic_name
        )
        cdk.Tags.of(features_failure_notification).add("a-nombre-recurso",
                                                       "sns")
        cdk.Tags.of(features_failure_notification).add("a-rol-servicio",
                                                       "no-aplica")

        self.log.info('Add subscriptions')
        for i in notifications_email:
            features_failure_notification.add_subscription(
                sns_subscriptions.EmailSubscription(email_address=i))

        print('Create trigger for SNS topic in case of failure of pipelines')

        pipeline_pattern = events.EventPattern(
            source=["aws.sagemaker"],
            detail_type=["SageMaker Pipeline Execution Status Change", ],
            detail={"currentPipelineExecutionStatus": [
                                                        "Failed"
                                                    ],
                    "pipelineArn": [
                                    f"{daneshapes_features_arn}"
                                    ]})

        pipelines_rule = events.Rule(
            self,
            id=self.rule_name,
            description='Detect failure in Mundos Training Performance',
            event_pattern=pipeline_pattern,
            rule_name=self.rule_name
            )
        event_status = events.EventField.from_path(
            '$.detail.currentPipelineExecutionStatus')
        pipelines_rule.add_target(
            events_targets.SnsTopic(
                topic=features_failure_notification,
                message=events.RuleTargetInput.from_text(
                    f"The SageMaker Pipeline "
                    f"{events.EventField.from_path('$.detail.pipelineArn')} "
                    f"has {event_status}")))
