"""Handles incoming shield requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import ShieldBackend, shield_backends


class ShieldResponse(BaseResponse):
    """Handler for Shield requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="shield")

    @property
    def shield_backend(self) -> ShieldBackend:
        """Return backend instance specific for this region."""
        return shield_backends[self.current_account][self.partition]

    def create_protection(self) -> str:
        params = json.loads(self.body)
        name = params.get("Name")
        resource_arn = params.get("ResourceArn")
        tags = params.get("Tags")
        protection_id = self.shield_backend.create_protection(
            name=name,
            resource_arn=resource_arn,
            tags=tags,
        )
        return json.dumps({"ProtectionId": protection_id})

    def describe_protection(self) -> str:
        params = json.loads(self.body)
        protection_id = params.get("ProtectionId")
        resource_arn = params.get("ResourceArn")
        protection = self.shield_backend.describe_protection(
            protection_id=protection_id,
            resource_arn=resource_arn,
        )
        return json.dumps({"Protection": protection.to_dict()})

    def list_protections(self) -> str:
        params = json.loads(self.body)
        inclusion_filters = params.get("InclusionFilters")
        protections = self.shield_backend.list_protections(
            inclusion_filters=inclusion_filters,
        )
        return json.dumps(
            {"Protections": [protection.to_dict() for protection in protections]}
        )

    def delete_protection(self) -> str:
        params = json.loads(self.body)
        protection_id = params.get("ProtectionId")
        self.shield_backend.delete_protection(
            protection_id=protection_id,
        )
        return "{}"

    def list_tags_for_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = self.shield_backend.list_tags_for_resource(
            resource_arn=resource_arn,
        )
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tags = params.get("Tags")
        self.shield_backend.tag_resource(
            resource_arn=resource_arn,
            tags=tags,
        )
        return "{}"

    def untag_resource(self) -> str:
        params = json.loads(self.body)
        resource_arn = params.get("ResourceARN")
        tag_keys = params.get("TagKeys")
        self.shield_backend.untag_resource(
            resource_arn=resource_arn,
            tag_keys=tag_keys,
        )
        return "{}"

    def create_subscription(self) -> str:
        self.shield_backend.create_subscription()
        return "{}"

    def describe_subscription(self) -> str:
        subscription = self.shield_backend.describe_subscription()
        return json.dumps({"Subscription": subscription.to_dict()})

    def delete_subscription(self) -> str:
        self.shield_backend.delete_subscription()
        return "{}"

    def update_subscription(self) -> str:
        params = json.loads(self.body)
        auto_renew = params.get("AutoRenew")
        self.shield_backend.update_subscription(auto_renew=auto_renew)
        return "{}"

    def get_subscription_state(self) -> str:
        state = self.shield_backend.get_subscription_state()
        return json.dumps({"SubscriptionState": state})

    # Protection Group operations

    def create_protection_group(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.create_protection_group(
            protection_group_id=params["ProtectionGroupId"],
            aggregation=params["Aggregation"],
            pattern=params["Pattern"],
            resource_type=params.get("ResourceType"),
            members=params.get("Members", []),
            tags=params.get("Tags", []),
        )
        return "{}"

    def describe_protection_group(self) -> str:
        params = json.loads(self.body)
        pg = self.shield_backend.describe_protection_group(
            protection_group_id=params["ProtectionGroupId"],
        )
        return json.dumps({"ProtectionGroup": pg.to_dict()})

    def update_protection_group(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.update_protection_group(
            protection_group_id=params["ProtectionGroupId"],
            aggregation=params["Aggregation"],
            pattern=params["Pattern"],
            resource_type=params.get("ResourceType"),
            members=params.get("Members"),
        )
        return "{}"

    def delete_protection_group(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.delete_protection_group(
            protection_group_id=params["ProtectionGroupId"],
        )
        return "{}"

    def list_protection_groups(self) -> str:
        params = json.loads(self.body)
        inclusion_filters = params.get("InclusionFilters")
        groups = self.shield_backend.list_protection_groups(
            inclusion_filters=inclusion_filters,
        )
        return json.dumps(
            {"ProtectionGroups": [g.to_dict() for g in groups]}
        )

    def list_resources_in_protection_group(self) -> str:
        params = json.loads(self.body)
        resource_arns = self.shield_backend.list_resources_in_protection_group(
            protection_group_id=params["ProtectionGroupId"],
        )
        return json.dumps({"ResourceArns": resource_arns})

    # Health check association

    def associate_health_check(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.associate_health_check(
            protection_id=params["ProtectionId"],
            health_check_arn=params["HealthCheckArn"],
        )
        return "{}"

    def disassociate_health_check(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.disassociate_health_check(
            protection_id=params["ProtectionId"],
            health_check_arn=params["HealthCheckArn"],
        )
        return "{}"

    # Application layer automatic response

    def enable_application_layer_automatic_response(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.enable_application_layer_automatic_response(
            resource_arn=params["ResourceArn"],
            action=params["Action"],
        )
        return "{}"

    def disable_application_layer_automatic_response(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.disable_application_layer_automatic_response(
            resource_arn=params["ResourceArn"],
        )
        return "{}"

    def update_application_layer_automatic_response(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.update_application_layer_automatic_response(
            resource_arn=params["ResourceArn"],
            action=params["Action"],
        )
        return "{}"

    # DRT access

    def associate_drt_role(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.associate_drt_role(role_arn=params["RoleArn"])
        return "{}"

    def disassociate_drt_role(self) -> str:
        self.shield_backend.disassociate_drt_role()
        return "{}"

    def associate_drt_log_bucket(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.associate_drt_log_bucket(
            log_bucket=params["LogBucket"],
        )
        return "{}"

    def disassociate_drt_log_bucket(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.disassociate_drt_log_bucket(
            log_bucket=params["LogBucket"],
        )
        return "{}"

    def describe_drt_access(self) -> str:
        result = self.shield_backend.describe_drt_access()
        return json.dumps(result)

    # Emergency contacts

    def update_emergency_contact_settings(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.update_emergency_contact_settings(
            emergency_contact_list=params.get("EmergencyContactList", []),
        )
        return "{}"

    def describe_emergency_contact_settings(self) -> str:
        contacts = self.shield_backend.describe_emergency_contact_settings()
        return json.dumps({"EmergencyContactList": contacts})

    def associate_proactive_engagement_details(self) -> str:
        params = json.loads(self.body)
        self.shield_backend.associate_proactive_engagement_details(
            emergency_contact_list=params.get("EmergencyContactList", []),
        )
        return "{}"

    # Proactive engagement

    def enable_proactive_engagement(self) -> str:
        self.shield_backend.enable_proactive_engagement()
        return "{}"

    def disable_proactive_engagement(self) -> str:
        self.shield_backend.disable_proactive_engagement()
        return "{}"

    # Attacks

    def describe_attack(self) -> str:
        params = json.loads(self.body)
        attack = self.shield_backend.describe_attack(
            attack_id=params["AttackId"],
        )
        return json.dumps({"Attack": attack})

    def list_attacks(self) -> str:
        attacks = self.shield_backend.list_attacks()
        return json.dumps({"AttackSummaries": attacks})

    def describe_attack_statistics(self) -> str:
        stats = self.shield_backend.describe_attack_statistics()
        return json.dumps(stats)
