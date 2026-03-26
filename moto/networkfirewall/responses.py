"""Handles incoming networkfirewall requests, invokes methods, returns responses."""

import json

from moto.core.responses import BaseResponse

from .models import NetworkFirewallBackend, networkfirewall_backends


class NetworkFirewallResponse(BaseResponse):
    """Handler for NetworkFirewall requests and responses."""

    def __init__(self) -> None:
        super().__init__(service_name="networkfirewall")

    @property
    def networkfirewall_backend(self) -> NetworkFirewallBackend:
        """Return backend instance specific for this region."""
        return networkfirewall_backends[self.current_account][self.region]

    def create_firewall(self) -> str:
        firewall_name = self._get_param("FirewallName")
        firewall_policy_arn = self._get_param("FirewallPolicyArn")
        vpc_id = self._get_param("VpcId")
        subnet_mappings = self._get_param("SubnetMappings")
        delete_protection = self._get_param("DeleteProtection")
        subnet_change_protection = self._get_param("SubnetChangeProtection")
        firewall_policy_change_protection = self._get_param("FirewallPolicyChangeProtection")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        encryption_configuration = self._get_param("EncryptionConfiguration")
        enabled_analysis_types = self._get_param("EnabledAnalysisTypes")
        firewall = self.networkfirewall_backend.create_firewall(
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
        return json.dumps(
            {"Firewall": firewall.to_dict(), "FirewallStatus": firewall.firewall_status}
        )

    def delete_firewall(self) -> str:
        firewall_name = self._get_param("FirewallName")
        firewall_arn = self._get_param("FirewallArn")
        firewall = self.networkfirewall_backend.delete_firewall(
            firewall_name=firewall_name,
            firewall_arn=firewall_arn,
        )
        return json.dumps(
            {"Firewall": firewall.to_dict(), "FirewallStatus": firewall.firewall_status}
        )

    def describe_firewall(self) -> str:
        firewall_name = self._get_param("FirewallName")
        firewall_arn = self._get_param("FirewallArn")
        firewall = self.networkfirewall_backend.describe_firewall(
            firewall_name=firewall_name,
            firewall_arn=firewall_arn,
        )
        return json.dumps(
            {
                "UpdateToken": firewall.update_token,
                "Firewall": firewall.to_dict(),
                "FirewallStatus": firewall.firewall_status,
            }
        )

    def describe_firewall_metadata(self) -> str:
        firewall_name = self._get_param("FirewallName")
        firewall_arn = self._get_param("FirewallArn")
        firewall = self.networkfirewall_backend.describe_firewall_metadata(
            firewall_name=firewall_name,
            firewall_arn=firewall_arn,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "FirewallPolicyArn": firewall.firewall_policy_arn,
                "VpcId": firewall.vpc_id,
                "Status": firewall.firewall_status.get("Status", "READY"),
            }
        )

    def describe_logging_configuration(self) -> str:
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        firewall = self.networkfirewall_backend.describe_logging_configuration(
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "LoggingConfiguration": firewall.logging_configs,
            }
        )

    def update_logging_configuration(self) -> str:
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        logging_configuration = self._get_param("LoggingConfiguration")
        firewall = self.networkfirewall_backend.update_logging_configuration(
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            logging_configuration=logging_configuration,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "LoggingConfiguration": firewall.logging_configs,
            }
        )

    def update_firewall_description(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        description = self._get_param("Description")
        firewall = self.networkfirewall_backend.update_firewall_description(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            description=description,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "Description": firewall.description,
                "UpdateToken": firewall.update_token,
            }
        )

    def update_firewall_delete_protection(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        delete_protection = self._get_param("DeleteProtection")
        firewall = self.networkfirewall_backend.update_firewall_delete_protection(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            delete_protection=delete_protection,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "DeleteProtection": firewall.delete_protection,
                "UpdateToken": firewall.update_token,
            }
        )

    def update_firewall_policy_change_protection(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        firewall_policy_change_protection = self._get_param("FirewallPolicyChangeProtection")
        firewall = self.networkfirewall_backend.update_firewall_policy_change_protection(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            firewall_policy_change_protection=firewall_policy_change_protection,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "FirewallPolicyChangeProtection": firewall.firewall_policy_change_protection,
                "UpdateToken": firewall.update_token,
            }
        )

    def update_subnet_change_protection(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        subnet_change_protection = self._get_param("SubnetChangeProtection")
        firewall = self.networkfirewall_backend.update_subnet_change_protection(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            subnet_change_protection=subnet_change_protection,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "SubnetChangeProtection": firewall.subnet_change_protection,
                "UpdateToken": firewall.update_token,
            }
        )

    def update_firewall_encryption_configuration(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        encryption_configuration = self._get_param("EncryptionConfiguration")
        firewall = self.networkfirewall_backend.update_firewall_encryption_configuration(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            encryption_configuration=encryption_configuration,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "UpdateToken": firewall.update_token,
                "EncryptionConfiguration": firewall.encryption_configuration,
            }
        )

    def associate_firewall_policy(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        firewall_policy_arn = self._get_param("FirewallPolicyArn")
        firewall = self.networkfirewall_backend.associate_firewall_policy(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            firewall_policy_arn=firewall_policy_arn,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "FirewallPolicyArn": firewall.firewall_policy_arn,
                "UpdateToken": firewall.update_token,
            }
        )

    def associate_subnets(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        subnet_mappings = self._get_param("SubnetMappings")
        firewall = self.networkfirewall_backend.associate_subnets(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            subnet_mappings=subnet_mappings,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "SubnetMappings": firewall.subnet_mappings,
                "UpdateToken": firewall.update_token,
            }
        )

    def disassociate_subnets(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        subnet_ids = self._get_param("SubnetIds")
        firewall = self.networkfirewall_backend.disassociate_subnets(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            subnet_ids=subnet_ids,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "SubnetMappings": firewall.subnet_mappings,
                "UpdateToken": firewall.update_token,
            }
        )

    def update_firewall_analysis_settings(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_arn = self._get_param("FirewallArn")
        firewall_name = self._get_param("FirewallName")
        enabled_analysis_types = self._get_param("EnabledAnalysisTypes")
        firewall = self.networkfirewall_backend.update_firewall_analysis_settings(
            update_token=update_token,
            firewall_arn=firewall_arn,
            firewall_name=firewall_name,
            enabled_analysis_types=enabled_analysis_types,
        )
        return json.dumps(
            {
                "FirewallArn": firewall.arn,
                "FirewallName": firewall.firewall_name,
                "EnabledAnalysisTypes": firewall.enabled_analysis_types,
                "UpdateToken": firewall.update_token,
            }
        )

    def list_firewalls(self) -> str:
        next_token = self._get_param("NextToken")
        vpc_ids = self._get_param("VpcIds")
        max_results = self._get_param("MaxResults")
        firewalls, next_token = self.networkfirewall_backend.list_firewalls(
            next_token=next_token,
            vpc_ids=vpc_ids,
            max_results=max_results,
        )
        firewall_list = [
            {"FirewallName": fw.firewall_name, "FirewallArn": fw.arn}
            for fw in firewalls
        ]
        return json.dumps({"NextToken": next_token, "Firewalls": firewall_list})

    def create_firewall_policy(self) -> str:
        firewall_policy_name = self._get_param("FirewallPolicyName")
        firewall_policy = self._get_param("FirewallPolicy")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        dry_run = self._get_param("DryRun") or False
        encryption_configuration = self._get_param("EncryptionConfiguration")
        policy = self.networkfirewall_backend.create_firewall_policy(
            firewall_policy_name=firewall_policy_name,
            firewall_policy=firewall_policy,
            description=description,
            tags=tags,
            dry_run=dry_run,
            encryption_configuration=encryption_configuration,
        )
        return json.dumps(
            {
                "UpdateToken": policy.update_token,
                "FirewallPolicyResponse": policy.to_detail_dict(),
            }
        )

    def delete_firewall_policy(self) -> str:
        firewall_policy_name = self._get_param("FirewallPolicyName")
        firewall_policy_arn = self._get_param("FirewallPolicyArn")
        policy = self.networkfirewall_backend.delete_firewall_policy(
            firewall_policy_name=firewall_policy_name,
            firewall_policy_arn=firewall_policy_arn,
        )
        return json.dumps({"FirewallPolicyResponse": policy.to_detail_dict()})

    def describe_firewall_policy(self) -> str:
        firewall_policy_name = self._get_param("FirewallPolicyName")
        firewall_policy_arn = self._get_param("FirewallPolicyArn")
        policy = self.networkfirewall_backend.describe_firewall_policy(
            firewall_policy_name=firewall_policy_name,
            firewall_policy_arn=firewall_policy_arn,
        )
        return json.dumps(
            {
                "UpdateToken": policy.update_token,
                "FirewallPolicy": policy.firewall_policy,
                "FirewallPolicyResponse": policy.to_detail_dict(),
            }
        )

    def update_firewall_policy(self) -> str:
        update_token = self._get_param("UpdateToken")
        firewall_policy_name = self._get_param("FirewallPolicyName")
        firewall_policy_arn = self._get_param("FirewallPolicyArn")
        firewall_policy = self._get_param("FirewallPolicy")
        description = self._get_param("Description")
        dry_run = self._get_param("DryRun") or False
        encryption_configuration = self._get_param("EncryptionConfiguration")
        policy = self.networkfirewall_backend.update_firewall_policy(
            update_token=update_token,
            firewall_policy_name=firewall_policy_name,
            firewall_policy_arn=firewall_policy_arn,
            firewall_policy=firewall_policy,
            description=description,
            dry_run=dry_run,
            encryption_configuration=encryption_configuration,
        )
        return json.dumps(
            {
                "UpdateToken": policy.update_token,
                "FirewallPolicyResponse": policy.to_detail_dict(),
            }
        )

    def list_firewall_policies(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        policies, next_token = self.networkfirewall_backend.list_firewall_policies(
            next_token=next_token,
            max_results=max_results,
        )
        policy_list = [{"Name": p.firewall_policy_name, "Arn": p.arn} for p in policies]
        return json.dumps({"NextToken": next_token, "FirewallPolicies": policy_list})

    def create_rule_group(self) -> str:
        rule_group_name = self._get_param("RuleGroupName")
        rule_group = self._get_param("RuleGroup")
        rule_group_type = self._get_param("Type")
        capacity = self._get_param("Capacity")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        rules = self._get_param("Rules")
        dry_run = self._get_param("DryRun") or False
        encryption_configuration = self._get_param("EncryptionConfiguration")
        source_metadata = self._get_param("SourceMetadata")
        analyze_rule_group = self._get_param("AnalyzeRuleGroup") or False
        rg = self.networkfirewall_backend.create_rule_group(
            rule_group_name=rule_group_name,
            rule_group=rule_group,
            rule_group_type=rule_group_type,
            capacity=capacity,
            description=description,
            tags=tags,
            rules=rules,
            dry_run=dry_run,
            encryption_configuration=encryption_configuration,
            source_metadata=source_metadata,
            analyze_rule_group=analyze_rule_group,
        )
        return json.dumps(
            {
                "UpdateToken": rg.update_token,
                "RuleGroupResponse": rg.to_metadata_dict(),
            }
        )

    def delete_rule_group(self) -> str:
        rule_group_name = self._get_param("RuleGroupName")
        rule_group_arn = self._get_param("RuleGroupArn")
        rule_group_type = self._get_param("Type")
        rg = self.networkfirewall_backend.delete_rule_group(
            rule_group_name=rule_group_name,
            rule_group_arn=rule_group_arn,
            rule_group_type=rule_group_type,
        )
        return json.dumps({"RuleGroupResponse": rg.to_metadata_dict()})

    def describe_rule_group(self) -> str:
        rule_group_name = self._get_param("RuleGroupName")
        rule_group_arn = self._get_param("RuleGroupArn")
        rule_group_type = self._get_param("Type")
        analyze_rule_group = self._get_param("AnalyzeRuleGroup") or False
        rg = self.networkfirewall_backend.describe_rule_group(
            rule_group_name=rule_group_name,
            rule_group_arn=rule_group_arn,
            rule_group_type=rule_group_type,
            analyze_rule_group=analyze_rule_group,
        )
        return json.dumps(
            {
                "UpdateToken": rg.update_token,
                "RuleGroup": rg.rule_group,
                "RuleGroupResponse": rg.to_metadata_dict(),
            }
        )

    def describe_rule_group_metadata(self) -> str:
        rule_group_name = self._get_param("RuleGroupName")
        rule_group_arn = self._get_param("RuleGroupArn")
        rule_group_type = self._get_param("Type")
        rg = self.networkfirewall_backend.describe_rule_group_metadata(
            rule_group_name=rule_group_name,
            rule_group_arn=rule_group_arn,
            rule_group_type=rule_group_type,
        )
        return json.dumps(rg.to_metadata_dict())

    def describe_rule_group_summary(self) -> str:
        rule_group_name = self._get_param("RuleGroupName")
        rule_group_arn = self._get_param("RuleGroupArn")
        rule_group_type = self._get_param("Type")
        rg = self.networkfirewall_backend.describe_rule_group_summary(
            rule_group_name=rule_group_name,
            rule_group_arn=rule_group_arn,
            rule_group_type=rule_group_type,
        )
        return json.dumps(rg.to_metadata_dict())

    def update_rule_group(self) -> str:
        update_token = self._get_param("UpdateToken")
        rule_group_arn = self._get_param("RuleGroupArn")
        rule_group_name = self._get_param("RuleGroupName")
        rule_group = self._get_param("RuleGroup")
        rules = self._get_param("Rules")
        rule_group_type = self._get_param("Type")
        description = self._get_param("Description")
        dry_run = self._get_param("DryRun") or False
        encryption_configuration = self._get_param("EncryptionConfiguration")
        source_metadata = self._get_param("SourceMetadata")
        analyze_rule_group = self._get_param("AnalyzeRuleGroup") or False
        rg = self.networkfirewall_backend.update_rule_group(
            update_token=update_token,
            rule_group_arn=rule_group_arn,
            rule_group_name=rule_group_name,
            rule_group=rule_group,
            rules=rules,
            rule_group_type=rule_group_type,
            description=description,
            dry_run=dry_run,
            encryption_configuration=encryption_configuration,
            source_metadata=source_metadata,
            analyze_rule_group=analyze_rule_group,
        )
        return json.dumps(
            {
                "UpdateToken": rg.update_token,
                "RuleGroupResponse": rg.to_metadata_dict(),
            }
        )

    def list_rule_groups(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        scope = self._get_param("Scope")
        managed_type = self._get_param("ManagedType")
        rule_group_type = self._get_param("Type")
        groups, next_token = self.networkfirewall_backend.list_rule_groups(
            next_token=next_token,
            max_results=max_results,
            scope=scope,
            managed_type=managed_type,
            rule_group_type=rule_group_type,
        )
        group_list = [{"Name": g.rule_group_name, "Arn": g.arn} for g in groups]
        return json.dumps({"NextToken": next_token, "RuleGroups": group_list})

    def create_tls_inspection_configuration(self) -> str:
        tls_inspection_configuration_name = self._get_param("TLSInspectionConfigurationName")
        tls_inspection_configuration = self._get_param("TLSInspectionConfiguration")
        description = self._get_param("Description")
        tags = self._get_param("Tags")
        encryption_configuration = self._get_param("EncryptionConfiguration")
        tls = self.networkfirewall_backend.create_tls_inspection_configuration(
            tls_inspection_configuration_name=tls_inspection_configuration_name,
            tls_inspection_configuration=tls_inspection_configuration,
            description=description,
            tags=tags,
            encryption_configuration=encryption_configuration,
        )
        return json.dumps(
            {
                "UpdateToken": tls.update_token,
                "TLSInspectionConfigurationResponse": tls.to_metadata_dict(),
            }
        )

    def delete_tls_inspection_configuration(self) -> str:
        tls_inspection_configuration_arn = self._get_param("TLSInspectionConfigurationArn")
        tls_inspection_configuration_name = self._get_param("TLSInspectionConfigurationName")
        tls = self.networkfirewall_backend.delete_tls_inspection_configuration(
            tls_inspection_configuration_arn=tls_inspection_configuration_arn,
            tls_inspection_configuration_name=tls_inspection_configuration_name,
        )
        return json.dumps({"TLSInspectionConfigurationResponse": tls.to_metadata_dict()})

    def describe_tls_inspection_configuration(self) -> str:
        tls_inspection_configuration_arn = self._get_param("TLSInspectionConfigurationArn")
        tls_inspection_configuration_name = self._get_param("TLSInspectionConfigurationName")
        tls = self.networkfirewall_backend.describe_tls_inspection_configuration(
            tls_inspection_configuration_arn=tls_inspection_configuration_arn,
            tls_inspection_configuration_name=tls_inspection_configuration_name,
        )
        return json.dumps(
            {
                "UpdateToken": tls.update_token,
                "TLSInspectionConfiguration": tls.tls_inspection_configuration,
                "TLSInspectionConfigurationResponse": tls.to_metadata_dict(),
            }
        )

    def update_tls_inspection_configuration(self) -> str:
        update_token = self._get_param("UpdateToken")
        tls_inspection_configuration_arn = self._get_param("TLSInspectionConfigurationArn")
        tls_inspection_configuration_name = self._get_param("TLSInspectionConfigurationName")
        tls_inspection_configuration = self._get_param("TLSInspectionConfiguration")
        description = self._get_param("Description")
        encryption_configuration = self._get_param("EncryptionConfiguration")
        tls = self.networkfirewall_backend.update_tls_inspection_configuration(
            update_token=update_token,
            tls_inspection_configuration_arn=tls_inspection_configuration_arn,
            tls_inspection_configuration_name=tls_inspection_configuration_name,
            tls_inspection_configuration=tls_inspection_configuration,
            description=description,
            encryption_configuration=encryption_configuration,
        )
        return json.dumps(
            {
                "UpdateToken": tls.update_token,
                "TLSInspectionConfigurationResponse": tls.to_metadata_dict(),
            }
        )

    def list_tls_inspection_configurations(self) -> str:
        next_token = self._get_param("NextToken")
        max_results = self._get_param("MaxResults")
        configs, next_token = self.networkfirewall_backend.list_tls_inspection_configurations(
            next_token=next_token,
            max_results=max_results,
        )
        config_list = [
            {"Name": c.tls_inspection_configuration_name, "Arn": c.arn}
            for c in configs
        ]
        return json.dumps(
            {"NextToken": next_token, "TLSInspectionConfigurations": config_list}
        )

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self.networkfirewall_backend.list_tags_for_resource(resource_arn)
        return json.dumps({"Tags": tags})

    def tag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tags = self._get_param("Tags")
        self.networkfirewall_backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        tag_keys = self._get_param("TagKeys")
        self.networkfirewall_backend.untag_resource(resource_arn, tag_keys)
        return json.dumps({})

    def put_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        policy = self._get_param("Policy")
        self.networkfirewall_backend.put_resource_policy(resource_arn, policy)
        return json.dumps({})

    def describe_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        policy = self.networkfirewall_backend.describe_resource_policy(resource_arn)
        return json.dumps({"Policy": policy})

    def delete_resource_policy(self) -> str:
        resource_arn = self._get_param("ResourceArn")
        self.networkfirewall_backend.delete_resource_policy(resource_arn)
        return json.dumps({})
