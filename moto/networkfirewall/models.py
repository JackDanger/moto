"""NetworkFirewallBackend class with methods for supported APIs."""

import uuid
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.networkfirewall.exceptions import ResourceInUse, ResourceNotFound
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService

PAGINATION_MODEL = {
    "list_firewalls": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_firewall_policies": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_rule_groups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
    "list_tls_inspection_configurations": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 100,
        "unique_attribute": "arn",
    },
}


def _new_update_token() -> str:
    return str(uuid.uuid4())


class FirewallPolicyModel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        firewall_policy_name: str,
        firewall_policy: dict[str, Any],
        description: str,
        tags: list[dict[str, str]],
        encryption_configuration: Optional[dict[str, str]],
    ):
        self.firewall_policy_name = firewall_policy_name
        self.firewall_policy = firewall_policy
        self.description = description or ""
        self.tags = tags or []
        self.encryption_configuration = encryption_configuration
        self.arn = f"arn:aws:network-firewall:{region_name}:{account_id}:firewall-policy/{firewall_policy_name}"
        self.update_token = _new_update_token()
        self.firewall_policy_status = "ACTIVE"

    def to_detail_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "FirewallPolicyName": self.firewall_policy_name,
            "FirewallPolicyArn": self.arn,
            "FirewallPolicyStatus": self.firewall_policy_status,
            "Description": self.description,
            "Tags": self.tags,
        }
        if self.encryption_configuration:
            result["EncryptionConfiguration"] = self.encryption_configuration
        return result


class RuleGroupModel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        rule_group_name: str,
        rule_group: Optional[dict[str, Any]],
        rule_group_type: str,
        capacity: int,
        description: str,
        tags: list[dict[str, str]],
        rules: Optional[str],
        encryption_configuration: Optional[dict[str, str]],
        source_metadata: Optional[dict[str, str]],
    ):
        self.rule_group_name = rule_group_name
        self.rule_group = rule_group or {}
        self.rule_group_type = rule_group_type
        self.capacity = capacity
        self.description = description or ""
        self.tags = tags or []
        self.rules = rules
        self.encryption_configuration = encryption_configuration
        self.source_metadata = source_metadata
        rg_prefix = "stateful-rulegroup" if rule_group_type == "STATEFUL" else "stateless-rulegroup"
        self.arn = f"arn:aws:network-firewall:{region_name}:{account_id}:{rg_prefix}/{rule_group_name}"
        self.update_token = _new_update_token()
        self.rule_group_status = "ACTIVE"

    def to_metadata_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "RuleGroupArn": self.arn,
            "RuleGroupName": self.rule_group_name,
            "RuleGroupStatus": self.rule_group_status,
            "Type": self.rule_group_type,
            "Capacity": self.capacity,
            "Description": self.description,
            "Tags": self.tags,
        }
        if self.encryption_configuration:
            result["EncryptionConfiguration"] = self.encryption_configuration
        if self.source_metadata:
            result["SourceMetadata"] = self.source_metadata
        return result


class TLSInspectionConfigurationModel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        tls_inspection_configuration_name: str,
        tls_inspection_configuration: dict[str, Any],
        description: str,
        tags: list[dict[str, str]],
        encryption_configuration: Optional[dict[str, str]],
    ):
        self.tls_inspection_configuration_name = tls_inspection_configuration_name
        self.tls_inspection_configuration = tls_inspection_configuration
        self.description = description or ""
        self.tags = tags or []
        self.encryption_configuration = encryption_configuration
        self.arn = f"arn:aws:network-firewall:{region_name}:{account_id}:tls-configuration/{tls_inspection_configuration_name}"
        self.update_token = _new_update_token()
        self.tls_inspection_configuration_status = "ACTIVE"

    def to_metadata_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "TLSInspectionConfigurationArn": self.arn,
            "TLSInspectionConfigurationName": self.tls_inspection_configuration_name,
            "TLSInspectionConfigurationStatus": self.tls_inspection_configuration_status,
            "Description": self.description,
            "Tags": self.tags,
        }
        if self.encryption_configuration:
            result["EncryptionConfiguration"] = self.encryption_configuration
        return result


class NetworkFirewallModel(BaseModel):
    def __init__(
        self,
        account_id: str,
        region_name: str,
        firewall_name: str,
        firewall_policy_arn: str,
        vpc_id: str,
        subnet_mappings: list[str],
        delete_protection: bool,
        subnet_change_protection: bool,
        firewall_policy_change_protection: bool,
        description: str,
        tags: list[dict[str, str]],
        encryption_configuration: dict[str, str],
        enabled_analysis_types: list[str],
    ):
        self.firewall_name = firewall_name
        self.firewall_policy_arn = firewall_policy_arn
        self.vpc_id = vpc_id
        self.subnet_mappings = subnet_mappings
        self.delete_protection: bool = (
            delete_protection if delete_protection is not None else True
        )
        self.subnet_change_protection: bool = (
            subnet_change_protection if subnet_change_protection is not None else True
        )
        self.firewall_policy_change_protection: bool = (
            firewall_policy_change_protection
            if firewall_policy_change_protection is not None
            else True
        )
        self.description = description
        self.tags = tags
        self.encryption_configuration = encryption_configuration
        self.enabled_analysis_types = enabled_analysis_types
        self.arn = f"arn:aws:network-firewall:{region_name}:{account_id}:firewall/{self.firewall_name}"
        self.update_token = _new_update_token()
        self.firewall_status = {
            "Status": "READY",
            "ConfigurationSyncStateSummary": "IN_SYNC",
        }
        self.logging_configs: dict[str, list[dict[str, Any]]] = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "FirewallName": self.firewall_name,
            "FirewallArn": self.arn,
            "FirewallPolicyArn": self.firewall_policy_arn,
            "VpcId": self.vpc_id,
            "SubnetMappings": self.subnet_mappings,
            "DeleteProtection": self.delete_protection,
            "SubnetChangeProtection": self.subnet_change_protection,
            "FirewallPolicyChangeProtection": self.firewall_policy_change_protection,
            "Description": self.description,
            "Tags": self.tags,
            "EncryptionConfiguration": self.encryption_configuration,
            "EnabledAnalysisTypes": self.enabled_analysis_types,
        }


class NetworkFirewallBackend(BaseBackend):
    """Implementation of NetworkFirewall APIs."""

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.firewalls: dict[str, NetworkFirewallModel] = {}
        self.firewall_policies: dict[str, FirewallPolicyModel] = {}
        self.rule_groups: dict[str, RuleGroupModel] = {}
        self.tls_inspection_configurations: dict[str, TLSInspectionConfigurationModel] = {}
        self.resource_policies: dict[str, str] = {}
        self.tagger = TaggingService()

    def create_firewall(
        self,
        firewall_name: str,
        firewall_policy_arn: str,
        vpc_id: str,
        subnet_mappings: list[str],
        delete_protection: bool,
        subnet_change_protection: bool,
        firewall_policy_change_protection: bool,
        description: str,
        tags: list[dict[str, str]],
        encryption_configuration: dict[str, str],
        enabled_analysis_types: list[str],
    ) -> NetworkFirewallModel:
        firewall = NetworkFirewallModel(
            self.account_id,
            self.region_name,
            firewall_name=firewall_name,
            firewall_policy_arn=firewall_policy_arn,
            vpc_id=vpc_id,
            subnet_mappings=subnet_mappings,
            delete_protection=delete_protection,
            subnet_change_protection=subnet_change_protection,
            firewall_policy_change_protection=firewall_policy_change_protection,
            description=description,
            tags=tags,
            encryption_configuration=encryption_configuration,
            enabled_analysis_types=enabled_analysis_types,
        )
        self.firewalls[firewall.arn] = firewall
        if tags:
            self.tagger.tag_resource(firewall.arn, tags)
        return firewall

    def _get_firewall(
        self, firewall_arn: Optional[str], firewall_name: Optional[str]
    ) -> NetworkFirewallModel:
        if firewall_arn and firewall_arn in self.firewalls:
            return self.firewalls[firewall_arn]
        for firewall in self.firewalls.values():
            if firewall.firewall_name == firewall_name:
                return firewall
        raise ResourceNotFound(str(firewall_arn or firewall_name))

    def delete_firewall(
        self, firewall_name: Optional[str], firewall_arn: Optional[str]
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        if firewall.delete_protection:
            raise ResourceInUse(
                f"Firewall {firewall.firewall_name} has delete protection enabled"
            )
        del self.firewalls[firewall.arn]
        return firewall

    def describe_firewall(
        self, firewall_name: str, firewall_arn: str
    ) -> NetworkFirewallModel:
        return self._get_firewall(firewall_arn, firewall_name)

    def describe_firewall_metadata(
        self, firewall_name: Optional[str], firewall_arn: Optional[str]
    ) -> NetworkFirewallModel:
        return self._get_firewall(firewall_arn, firewall_name)

    def describe_logging_configuration(
        self, firewall_arn: str, firewall_name: str
    ) -> NetworkFirewallModel:
        return self._get_firewall(firewall_arn, firewall_name)

    def update_logging_configuration(
        self,
        firewall_arn: str,
        firewall_name: str,
        logging_configuration: dict[str, list[dict[str, Any]]],
    ) -> NetworkFirewallModel:
        firewall: NetworkFirewallModel = self._get_firewall(firewall_arn, firewall_name)
        firewall.logging_configs = logging_configuration
        return firewall

    def update_firewall_description(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        description: str,
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.description = description
        firewall.update_token = _new_update_token()
        return firewall

    def update_firewall_delete_protection(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        delete_protection: bool,
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.delete_protection = delete_protection
        firewall.update_token = _new_update_token()
        return firewall

    def update_firewall_policy_change_protection(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        firewall_policy_change_protection: bool,
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.firewall_policy_change_protection = firewall_policy_change_protection
        firewall.update_token = _new_update_token()
        return firewall

    def update_subnet_change_protection(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        subnet_change_protection: bool,
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.subnet_change_protection = subnet_change_protection
        firewall.update_token = _new_update_token()
        return firewall

    def update_firewall_encryption_configuration(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        encryption_configuration: Optional[dict[str, str]],
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.encryption_configuration = encryption_configuration  # type: ignore[assignment]
        firewall.update_token = _new_update_token()
        return firewall

    def associate_firewall_policy(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        firewall_policy_arn: str,
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        if firewall.firewall_policy_change_protection:
            raise ResourceInUse(
                f"Firewall {firewall.firewall_name} has firewall policy change protection enabled"
            )
        firewall.firewall_policy_arn = firewall_policy_arn
        firewall.update_token = _new_update_token()
        return firewall

    def associate_subnets(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        subnet_mappings: list[dict[str, Any]],
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        existing_ids = {
            s.get("SubnetId") if isinstance(s, dict) else s
            for s in firewall.subnet_mappings
        }
        for s in subnet_mappings:
            sid = s.get("SubnetId") if isinstance(s, dict) else s
            if sid not in existing_ids:
                firewall.subnet_mappings.append(s)
        firewall.update_token = _new_update_token()
        return firewall

    def disassociate_subnets(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        subnet_ids: list[str],
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        firewall.subnet_mappings = [
            s
            for s in firewall.subnet_mappings
            if (s.get("SubnetId") if isinstance(s, dict) else s) not in subnet_ids
        ]
        firewall.update_token = _new_update_token()
        return firewall

    def update_firewall_analysis_settings(
        self,
        update_token: Optional[str],
        firewall_arn: Optional[str],
        firewall_name: Optional[str],
        enabled_analysis_types: Optional[list[str]],
    ) -> NetworkFirewallModel:
        firewall = self._get_firewall(firewall_arn, firewall_name)
        if enabled_analysis_types is not None:
            firewall.enabled_analysis_types = enabled_analysis_types
        firewall.update_token = _new_update_token()
        return firewall

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_firewalls(self, vpc_ids: list[str]) -> list[NetworkFirewallModel]:
        firewalls = list(self.firewalls.values())
        if vpc_ids:
            firewalls = [fw for fw in firewalls if fw.vpc_id in vpc_ids]
        return firewalls

    def create_firewall_policy(
        self,
        firewall_policy_name: str,
        firewall_policy: dict[str, Any],
        description: str,
        tags: list[dict[str, str]],
        dry_run: bool,
        encryption_configuration: Optional[dict[str, str]],
    ) -> FirewallPolicyModel:
        policy = FirewallPolicyModel(
            account_id=self.account_id,
            region_name=self.region_name,
            firewall_policy_name=firewall_policy_name,
            firewall_policy=firewall_policy,
            description=description,
            tags=tags,
            encryption_configuration=encryption_configuration,
        )
        if not dry_run:
            self.firewall_policies[policy.arn] = policy
            if tags:
                self.tagger.tag_resource(policy.arn, tags)
        return policy

    def _get_firewall_policy(
        self, firewall_policy_arn: Optional[str], firewall_policy_name: Optional[str]
    ) -> FirewallPolicyModel:
        if firewall_policy_arn and firewall_policy_arn in self.firewall_policies:
            return self.firewall_policies[firewall_policy_arn]
        for policy in self.firewall_policies.values():
            if policy.firewall_policy_name == firewall_policy_name:
                return policy
        raise ResourceNotFound(str(firewall_policy_arn or firewall_policy_name))

    def delete_firewall_policy(
        self,
        firewall_policy_name: Optional[str],
        firewall_policy_arn: Optional[str],
    ) -> FirewallPolicyModel:
        policy = self._get_firewall_policy(firewall_policy_arn, firewall_policy_name)
        for fw in self.firewalls.values():
            if fw.firewall_policy_arn == policy.arn:
                raise ResourceInUse(
                    f"Firewall policy {policy.firewall_policy_name} is in use by firewall {fw.firewall_name}"
                )
        del self.firewall_policies[policy.arn]
        return policy

    def describe_firewall_policy(
        self,
        firewall_policy_name: Optional[str],
        firewall_policy_arn: Optional[str],
    ) -> FirewallPolicyModel:
        return self._get_firewall_policy(firewall_policy_arn, firewall_policy_name)

    def update_firewall_policy(
        self,
        update_token: Optional[str],
        firewall_policy_name: Optional[str],
        firewall_policy_arn: Optional[str],
        firewall_policy: dict[str, Any],
        description: Optional[str],
        dry_run: bool,
        encryption_configuration: Optional[dict[str, str]],
    ) -> FirewallPolicyModel:
        policy = self._get_firewall_policy(firewall_policy_arn, firewall_policy_name)
        if not dry_run:
            policy.firewall_policy = firewall_policy
            if description is not None:
                policy.description = description
            if encryption_configuration is not None:
                policy.encryption_configuration = encryption_configuration
            policy.update_token = _new_update_token()
        return policy

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_firewall_policies(self) -> list[FirewallPolicyModel]:
        return list(self.firewall_policies.values())

    def create_rule_group(
        self,
        rule_group_name: str,
        rule_group: Optional[dict[str, Any]],
        rule_group_type: str,
        capacity: int,
        description: str,
        tags: list[dict[str, str]],
        rules: Optional[str],
        dry_run: bool,
        encryption_configuration: Optional[dict[str, str]],
        source_metadata: Optional[dict[str, str]],
        analyze_rule_group: bool,
    ) -> RuleGroupModel:
        rg = RuleGroupModel(
            account_id=self.account_id,
            region_name=self.region_name,
            rule_group_name=rule_group_name,
            rule_group=rule_group,
            rule_group_type=rule_group_type,
            capacity=capacity,
            description=description,
            tags=tags,
            rules=rules,
            encryption_configuration=encryption_configuration,
            source_metadata=source_metadata,
        )
        if not dry_run:
            self.rule_groups[rg.arn] = rg
            if tags:
                self.tagger.tag_resource(rg.arn, tags)
        return rg

    def _get_rule_group(
        self,
        rule_group_arn: Optional[str],
        rule_group_name: Optional[str],
        rule_group_type: Optional[str] = None,
    ) -> RuleGroupModel:
        if rule_group_arn and rule_group_arn in self.rule_groups:
            return self.rule_groups[rule_group_arn]
        for rg in self.rule_groups.values():
            if rg.rule_group_name == rule_group_name:
                if rule_group_type is None or rg.rule_group_type == rule_group_type:
                    return rg
        raise ResourceNotFound(str(rule_group_arn or rule_group_name))

    def delete_rule_group(
        self,
        rule_group_name: Optional[str],
        rule_group_arn: Optional[str],
        rule_group_type: Optional[str],
    ) -> RuleGroupModel:
        rg = self._get_rule_group(rule_group_arn, rule_group_name, rule_group_type)
        del self.rule_groups[rg.arn]
        return rg

    def describe_rule_group(
        self,
        rule_group_name: Optional[str],
        rule_group_arn: Optional[str],
        rule_group_type: Optional[str],
        analyze_rule_group: bool,
    ) -> RuleGroupModel:
        return self._get_rule_group(rule_group_arn, rule_group_name, rule_group_type)

    def describe_rule_group_metadata(
        self,
        rule_group_name: Optional[str],
        rule_group_arn: Optional[str],
        rule_group_type: Optional[str],
    ) -> RuleGroupModel:
        return self._get_rule_group(rule_group_arn, rule_group_name, rule_group_type)

    def describe_rule_group_summary(
        self,
        rule_group_name: Optional[str],
        rule_group_arn: Optional[str],
        rule_group_type: Optional[str],
    ) -> RuleGroupModel:
        return self._get_rule_group(rule_group_arn, rule_group_name, rule_group_type)

    def update_rule_group(
        self,
        update_token: Optional[str],
        rule_group_arn: Optional[str],
        rule_group_name: Optional[str],
        rule_group: Optional[dict[str, Any]],
        rules: Optional[str],
        rule_group_type: Optional[str],
        description: Optional[str],
        dry_run: bool,
        encryption_configuration: Optional[dict[str, str]],
        source_metadata: Optional[dict[str, str]],
        analyze_rule_group: bool,
    ) -> RuleGroupModel:
        rg = self._get_rule_group(rule_group_arn, rule_group_name, rule_group_type)
        if not dry_run:
            if rule_group is not None:
                rg.rule_group = rule_group
            if rules is not None:
                rg.rules = rules
            if description is not None:
                rg.description = description
            if encryption_configuration is not None:
                rg.encryption_configuration = encryption_configuration
            if source_metadata is not None:
                rg.source_metadata = source_metadata
            rg.update_token = _new_update_token()
        return rg

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_rule_groups(
        self,
        scope: Optional[str] = None,
        managed_type: Optional[str] = None,
        rule_group_type: Optional[str] = None,
    ) -> list[RuleGroupModel]:
        groups = list(self.rule_groups.values())
        if rule_group_type:
            groups = [g for g in groups if g.rule_group_type == rule_group_type]
        return groups

    def create_tls_inspection_configuration(
        self,
        tls_inspection_configuration_name: str,
        tls_inspection_configuration: dict[str, Any],
        description: str,
        tags: list[dict[str, str]],
        encryption_configuration: Optional[dict[str, str]],
    ) -> TLSInspectionConfigurationModel:
        tls = TLSInspectionConfigurationModel(
            account_id=self.account_id,
            region_name=self.region_name,
            tls_inspection_configuration_name=tls_inspection_configuration_name,
            tls_inspection_configuration=tls_inspection_configuration,
            description=description,
            tags=tags,
            encryption_configuration=encryption_configuration,
        )
        self.tls_inspection_configurations[tls.arn] = tls
        if tags:
            self.tagger.tag_resource(tls.arn, tags)
        return tls

    def _get_tls_inspection_configuration(
        self,
        tls_inspection_configuration_arn: Optional[str],
        tls_inspection_configuration_name: Optional[str],
    ) -> TLSInspectionConfigurationModel:
        if (
            tls_inspection_configuration_arn
            and tls_inspection_configuration_arn in self.tls_inspection_configurations
        ):
            return self.tls_inspection_configurations[tls_inspection_configuration_arn]
        for tls in self.tls_inspection_configurations.values():
            if tls.tls_inspection_configuration_name == tls_inspection_configuration_name:
                return tls
        raise ResourceNotFound(
            str(tls_inspection_configuration_arn or tls_inspection_configuration_name)
        )

    def delete_tls_inspection_configuration(
        self,
        tls_inspection_configuration_arn: Optional[str],
        tls_inspection_configuration_name: Optional[str],
    ) -> TLSInspectionConfigurationModel:
        tls = self._get_tls_inspection_configuration(
            tls_inspection_configuration_arn, tls_inspection_configuration_name
        )
        del self.tls_inspection_configurations[tls.arn]
        return tls

    def describe_tls_inspection_configuration(
        self,
        tls_inspection_configuration_arn: Optional[str],
        tls_inspection_configuration_name: Optional[str],
    ) -> TLSInspectionConfigurationModel:
        return self._get_tls_inspection_configuration(
            tls_inspection_configuration_arn, tls_inspection_configuration_name
        )

    def update_tls_inspection_configuration(
        self,
        update_token: Optional[str],
        tls_inspection_configuration_arn: Optional[str],
        tls_inspection_configuration_name: Optional[str],
        tls_inspection_configuration: dict[str, Any],
        description: Optional[str],
        encryption_configuration: Optional[dict[str, str]],
    ) -> TLSInspectionConfigurationModel:
        tls = self._get_tls_inspection_configuration(
            tls_inspection_configuration_arn, tls_inspection_configuration_name
        )
        tls.tls_inspection_configuration = tls_inspection_configuration
        if description is not None:
            tls.description = description
        if encryption_configuration is not None:
            tls.encryption_configuration = encryption_configuration
        tls.update_token = _new_update_token()
        return tls

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_tls_inspection_configurations(self) -> list[TLSInspectionConfigurationModel]:
        return list(self.tls_inspection_configurations.values())

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        return self.tagger.list_tags_for_resource(resource_arn)["Tags"]

    def tag_resource(self, resource_arn: str, tags: list[dict[str, str]]) -> None:
        self.tagger.tag_resource(resource_arn, tags)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        self.tagger.untag_resource(resource_arn, tag_keys)

    def put_resource_policy(self, resource_arn: str, policy: str) -> None:
        self.resource_policies[resource_arn] = policy

    def describe_resource_policy(self, resource_arn: str) -> Optional[str]:
        policy = self.resource_policies.get(resource_arn)
        if policy is None:
            raise ResourceNotFound(resource_arn)
        return policy

    def delete_resource_policy(self, resource_arn: str) -> None:
        if resource_arn not in self.resource_policies:
            raise ResourceNotFound(resource_arn)
        del self.resource_policies[resource_arn]


networkfirewall_backends = BackendDict(NetworkFirewallBackend, "network-firewall")
