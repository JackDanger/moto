import random
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.utilities.paginator import paginate
from moto.utilities.tagging_service import TaggingService
from moto.vpclattice.exceptions import (
    ResourceNotFoundException,
    ValidationException,
)


class VPCLatticeService(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        auth_type: str,
        certificate_arn: Optional[str],
        client_token: str,
        custom_domain_name: Optional[str],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> None:
        self.id: str = f"svc-{str(uuid.uuid4())[:17]}"
        self.auth_type: str = auth_type
        self.certificate_arn: str = certificate_arn or ""
        self.client_token: str = client_token
        self.custom_domain_name: str = custom_domain_name or ""
        self.dns_entry: VPCLatticeDNSEntry = VPCLatticeDNSEntry(
            region, self.id, self.custom_domain_name
        )
        self.name: str = name
        self.arn: str = f"arn:aws:vpc-lattice:{region}:{account_id}:service/{self.id}"
        self.status: str = "ACTIVE"
        self.tags: dict[str, str] = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "authType": self.auth_type,
            "certificateArn": self.certificate_arn,
            "customDomainName": self.custom_domain_name,
            "dnsEntry": self.dns_entry.to_dict(),
            "id": self.id,
            "name": self.name,
            "status": self.status,
        }


class VPCLatticeServiceNetwork(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        auth_type: str,
        client_token: str,
        name: str,
        sharing_config: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> None:
        self.auth_type: str = auth_type
        self.client_token: str = client_token
        self.id: str = f"sn-{str(uuid.uuid4())[:17]}"
        self.name: str = name
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:servicenetwork/{self.id}"
        )
        self.sharing_config: dict[str, Any] = sharing_config or {}
        self.tags: dict[str, str] = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "authType": self.auth_type,
            "id": self.id,
            "name": self.name,
            "sharingConfig": self.sharing_config,
        }


class VPCLatticeServiceNetworkVpcAssociation(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        client_token: str,
        security_group_ids: Optional[list[str]],
        service_network_identifier: str,
        tags: Optional[dict[str, str]],
        vpc_identifier: str,
    ) -> None:
        self.id: str = f"snva-{str(uuid.uuid4())[:17]}"
        self.arn: str = f"arn:aws:vpc-lattice:{region}:{account_id}:servicenetworkvpcassociation/{self.id}"
        self.created_by: str = "user"
        self.security_group_ids: list[str] = security_group_ids or []
        self.service_network_id: str = service_network_identifier
        self.vpc_id: str = vpc_identifier
        self.status: str = "ACTIVE"
        self.tags: dict[str, str] = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdBy": self.created_by,
            "id": self.id,
            "securityGroupIds": self.security_group_ids,
            "serviceNetworkId": self.service_network_id,
            "vpcId": self.vpc_id,
            "status": self.status,
        }


class VPCLatticeServiceNetworkServiceAssociation(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        client_token: str,
        service_identifier: str,
        service_network_identifier: str,
        tags: Optional[dict[str, str]],
    ) -> None:
        self.id: str = f"snsa-{str(uuid.uuid4())[:17]}"
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:servicenetworkserviceassociation/{self.id}"
        )
        self.created_by: str = "user"
        self.service_id: str = service_identifier
        self.service_network_id: str = service_network_identifier
        self.status: str = "ACTIVE"
        self.tags: dict[str, str] = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdBy": self.created_by,
            "id": self.id,
            "serviceId": self.service_id,
            "serviceNetworkId": self.service_network_id,
            "status": self.status,
        }


class VPCLatticeListener(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        client_token: str,
        default_action: dict[str, Any],
        name: str,
        port: Optional[int],
        protocol: str,
        service_identifier: str,
        tags: Optional[dict[str, str]],
    ) -> None:
        self.id: str = f"listener-{str(uuid.uuid4())[:17]}"
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:service/{service_identifier}/listener/{self.id}"
        )
        self.client_token: str = client_token
        self.default_action: dict[str, Any] = default_action or {}
        self.name: str = name
        self.port: Optional[int] = port or (443 if protocol == "HTTPS" else 80)
        self.protocol: str = protocol
        self.service_id: str = service_identifier
        self.status: str = "ACTIVE"
        self.tags: dict[str, str] = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "defaultAction": self.default_action,
            "id": self.id,
            "name": self.name,
            "port": self.port,
            "protocol": self.protocol,
            "serviceId": self.service_id,
            "status": self.status,
        }


class VPCLatticeRule(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        action: dict[str, Any],
        client_token: str,
        listener_identifier: str,
        match: dict[str, Any],
        name: str,
        priority: int,
        service_identifier: str,
        tags: dict[str, str],
    ) -> None:
        self.action: dict[str, Any] = action or {}
        self.id: str = f"rule-{str(uuid.uuid4())[:17]}"
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:service/{service_identifier}"
            f"/listener/{listener_identifier}/rule/{self.id}"
        )
        self.client_token: str = client_token
        self.listener_identifier: str = listener_identifier
        self.match: dict[str, Any] = match or {}
        self.name: str = name
        self.priority: int = priority
        self.service_identifier: str = service_identifier
        self.tags: dict[str, str] = tags or {}
        self.is_default: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "action": self.action,
            "match": self.match,
            "isDefault": self.is_default,
        }


class VPCLatticeTargetGroup(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        client_token: str,
        config: Optional[dict[str, Any]],
        name: str,
        tg_type: str,
        tags: Optional[dict[str, str]],
    ) -> None:
        self.id: str = f"tg-{str(uuid.uuid4())[:17]}"
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:targetgroup/{self.id}"
        )
        self.client_token: str = client_token
        self.config: dict[str, Any] = config or {}
        self.name: str = name
        self.type: str = tg_type
        self.status: str = "ACTIVE"
        self.tags: dict[str, str] = tags or {}
        self.targets: list[dict[str, Any]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "config": self.config,
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "type": self.type,
        }


class VPCLatticeDNSEntry:
    def __init__(
        self,
        region_name: str,
        service_id: str,
        custom_domain_name: Optional[str] = None,
    ) -> None:
        self.domain_name: str = (
            custom_domain_name or f"{service_id}.{region_name}.vpclattice.amazonaws.com"
        )
        self.hosted_zone_id: str = f"Z{random.randint(100000, 999999)}XYZ"

    def to_dict(self) -> dict[str, str]:
        return {"domainName": self.domain_name, "hostedZoneId": self.hosted_zone_id}


class VPCLatticeAccessLogSubscription(BaseModel):
    def __init__(
        self,
        region: str,
        account_id: str,
        destinationArn: str,
        resourceArn: str,
        resourceId: str,  # resourceIdentifier
        serviceNetworkLogType: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> None:
        self.id: str = f"als-{str(uuid.uuid4())[:17]}"
        self.arn: str = (
            f"arn:aws:vpc-lattice:{region}:{account_id}:accesslogsubscription/{self.id}"
        )
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.destinationArn = destinationArn
        self.last_updated_at = datetime.now(timezone.utc).isoformat()
        self.resourceArn = resourceArn
        self.resourceId = resourceId
        self.serviceNetworkLogType = serviceNetworkLogType or "SERVICE"
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "arn": self.arn,
            "createdAt": self.created_at,
            "destinationArn": self.destinationArn,
            "id": self.id,
            "lastUpdatedAt": self.last_updated_at,
            "resourceArn": self.resourceArn,
            "resourceId": self.resourceId,
            "serviceNetworkLogType": self.serviceNetworkLogType,
            "tags": self.tags,
        }


class AuthPolicy:
    def __init__(
        self,
        policy_name: str,
        policy: str,
        created_at: str,
        last_updated_at: str,
        state: str,
    ) -> None:
        self.policy_name = policy_name
        self.policy = policy
        self.created_at = created_at
        self.last_updated_at = last_updated_at
        self.state = state


class VPCLatticeBackend(BaseBackend):
    PAGINATION_MODEL = {
        "list_services": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 50,
            "unique_attribute": "id",
        },
        "list_service_networks": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 50,
            "unique_attribute": "id",
        },
        "list_target_groups": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_listeners": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_rules": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_service_network_service_associations": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_service_network_vpc_associations": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
        "list_targets": {
            "input_token": "next_token",
            "limit_key": "max_results",
            "limit_default": 100,
            "unique_attribute": "id",
        },
    }

    def __init__(self, region_name: str, account_id: str) -> None:
        super().__init__(region_name, account_id)
        self.services: dict[str, VPCLatticeService] = {}
        self.service_networks: dict[str, VPCLatticeServiceNetwork] = {}
        self.service_network_vpc_associations: dict[
            str, VPCLatticeServiceNetworkVpcAssociation
        ] = {}
        self.service_network_service_associations: dict[
            str, VPCLatticeServiceNetworkServiceAssociation
        ] = {}
        self.listeners: dict[str, VPCLatticeListener] = {}
        self.rules: dict[str, VPCLatticeRule] = {}
        self.target_groups: dict[str, VPCLatticeTargetGroup] = {}
        self.tagger: TaggingService = TaggingService()
        self.access_log_subscriptions: dict[str, VPCLatticeAccessLogSubscription] = {}
        self.resource_policies: dict[str, str] = {}
        self.auth_policies: dict[str, AuthPolicy] = {}

    # ---- Services ----

    def create_service(
        self,
        auth_type: str,
        certificate_arn: Optional[str],
        client_token: str,
        custom_domain_name: Optional[str],
        name: str,
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeService:
        service = VPCLatticeService(
            self.region_name,
            self.account_id,
            auth_type,
            certificate_arn,
            client_token,
            custom_domain_name,
            name,
            tags,
        )
        self.services[service.id] = service
        self.tag_resource(service.arn, tags or {})
        return service

    def get_service(self, service_identifier: str) -> VPCLatticeService:
        service = self.services.get(service_identifier)
        if not service:
            # try by name
            for svc in self.services.values():
                if svc.name == service_identifier or svc.arn == service_identifier:
                    return svc
            raise ResourceNotFoundException(service_identifier)
        return service

    def delete_service(self, service_identifier: str) -> VPCLatticeService:
        service = self.get_service(service_identifier)
        del self.services[service.id]
        return service

    def update_service(
        self,
        service_identifier: str,
        auth_type: Optional[str],
        certificate_arn: Optional[str],
    ) -> VPCLatticeService:
        service = self.get_service(service_identifier)
        if auth_type is not None:
            service.auth_type = auth_type
        if certificate_arn is not None:
            service.certificate_arn = certificate_arn
        return service

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_services(self) -> list[VPCLatticeService]:
        return list(self.services.values())

    # ---- Service Networks ----

    def create_service_network(
        self,
        auth_type: str,
        client_token: str,
        name: str,
        sharing_config: Optional[dict[str, Any]],
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeServiceNetwork:
        """
        WARNING: This method currently does NOT fail if there is a disassociation in progress.
        """
        sn = VPCLatticeServiceNetwork(
            self.region_name,
            self.account_id,
            auth_type,
            client_token,
            name,
            sharing_config,
            tags,
        )
        self.service_networks[sn.id] = sn
        self.tag_resource(sn.arn, tags or {})
        return sn

    def get_service_network(
        self, service_network_identifier: str
    ) -> VPCLatticeServiceNetwork:
        service_network = self.service_networks.get(service_network_identifier)
        if not service_network:
            # try by name or arn
            for sn in self.service_networks.values():
                if sn.name == service_network_identifier or sn.arn == service_network_identifier:
                    return sn
            raise ResourceNotFoundException(service_network_identifier)
        return service_network

    def delete_service_network(
        self, service_network_identifier: str
    ) -> None:
        sn = self.get_service_network(service_network_identifier)
        del self.service_networks[sn.id]

    def update_service_network(
        self,
        service_network_identifier: str,
        auth_type: str,
    ) -> VPCLatticeServiceNetwork:
        sn = self.get_service_network(service_network_identifier)
        sn.auth_type = auth_type
        return sn

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_service_networks(self) -> list[VPCLatticeServiceNetwork]:
        return list(self.service_networks.values())

    # ---- Service Network VPC Associations ----

    def create_service_network_vpc_association(
        self,
        client_token: str,
        security_group_ids: Optional[list[str]],
        service_network_identifier: str,
        tags: Optional[dict[str, str]],
        vpc_identifier: str,
    ) -> VPCLatticeServiceNetworkVpcAssociation:
        assoc = VPCLatticeServiceNetworkVpcAssociation(
            self.region_name,
            self.account_id,
            client_token,
            security_group_ids,
            service_network_identifier,
            tags,
            vpc_identifier,
        )
        self.service_network_vpc_associations[assoc.id] = assoc
        self.tag_resource(assoc.arn, tags or {})
        return assoc

    def get_service_network_vpc_association(
        self, service_network_vpc_association_identifier: str
    ) -> VPCLatticeServiceNetworkVpcAssociation:
        assoc = self.service_network_vpc_associations.get(
            service_network_vpc_association_identifier
        )
        if not assoc:
            raise ResourceNotFoundException(service_network_vpc_association_identifier)
        return assoc

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_service_network_vpc_associations(
        self,
        service_network_identifier: Optional[str] = None,
        vpc_identifier: Optional[str] = None,
    ) -> list[VPCLatticeServiceNetworkVpcAssociation]:
        results = list(self.service_network_vpc_associations.values())
        if service_network_identifier:
            results = [
                a for a in results
                if a.service_network_id == service_network_identifier
            ]
        if vpc_identifier:
            results = [a for a in results if a.vpc_id == vpc_identifier]
        return results

    def update_service_network_vpc_association(
        self,
        service_network_vpc_association_identifier: str,
        security_group_ids: list[str],
    ) -> VPCLatticeServiceNetworkVpcAssociation:
        assoc = self.get_service_network_vpc_association(
            service_network_vpc_association_identifier
        )
        assoc.security_group_ids = security_group_ids
        return assoc

    def delete_service_network_vpc_association(
        self, service_network_vpc_association_identifier: str
    ) -> VPCLatticeServiceNetworkVpcAssociation:
        assoc = self.get_service_network_vpc_association(
            service_network_vpc_association_identifier
        )
        assoc.status = "DELETE_IN_PROGRESS"
        del self.service_network_vpc_associations[assoc.id]
        return assoc

    # ---- Service Network Service Associations ----

    def create_service_network_service_association(
        self,
        client_token: str,
        service_identifier: str,
        service_network_identifier: str,
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeServiceNetworkServiceAssociation:
        assoc = VPCLatticeServiceNetworkServiceAssociation(
            self.region_name,
            self.account_id,
            client_token,
            service_identifier,
            service_network_identifier,
            tags,
        )
        self.service_network_service_associations[assoc.id] = assoc
        self.tag_resource(assoc.arn, tags or {})
        return assoc

    def get_service_network_service_association(
        self, service_network_service_association_identifier: str
    ) -> VPCLatticeServiceNetworkServiceAssociation:
        assoc = self.service_network_service_associations.get(
            service_network_service_association_identifier
        )
        if not assoc:
            raise ResourceNotFoundException(
                service_network_service_association_identifier
            )
        return assoc

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_service_network_service_associations(
        self,
        service_network_identifier: Optional[str] = None,
        service_identifier: Optional[str] = None,
    ) -> list[VPCLatticeServiceNetworkServiceAssociation]:
        results = list(self.service_network_service_associations.values())
        if service_network_identifier:
            results = [
                a for a in results
                if a.service_network_id == service_network_identifier
            ]
        if service_identifier:
            results = [a for a in results if a.service_id == service_identifier]
        return results

    def delete_service_network_service_association(
        self, service_network_service_association_identifier: str
    ) -> VPCLatticeServiceNetworkServiceAssociation:
        assoc = self.get_service_network_service_association(
            service_network_service_association_identifier
        )
        del self.service_network_service_associations[assoc.id]
        return assoc

    # ---- Listeners ----

    def create_listener(
        self,
        client_token: str,
        default_action: dict[str, Any],
        name: str,
        port: Optional[int],
        protocol: str,
        service_identifier: str,
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeListener:
        # validate service exists
        self.get_service(service_identifier)
        listener = VPCLatticeListener(
            self.region_name,
            self.account_id,
            client_token,
            default_action,
            name,
            port,
            protocol,
            service_identifier,
            tags,
        )
        self.listeners[listener.id] = listener
        self.tag_resource(listener.arn, tags or {})
        return listener

    def get_listener(
        self, service_identifier: str, listener_identifier: str
    ) -> VPCLatticeListener:
        listener = self.listeners.get(listener_identifier)
        if not listener:
            raise ResourceNotFoundException(listener_identifier)
        return listener

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_listeners(
        self, service_identifier: str
    ) -> list[VPCLatticeListener]:
        return [
            lst for lst in self.listeners.values()
            if lst.service_id == service_identifier
        ]

    def update_listener(
        self,
        service_identifier: str,
        listener_identifier: str,
        default_action: dict[str, Any],
    ) -> VPCLatticeListener:
        listener = self.get_listener(service_identifier, listener_identifier)
        listener.default_action = default_action
        return listener

    def delete_listener(
        self, service_identifier: str, listener_identifier: str
    ) -> None:
        self.get_listener(service_identifier, listener_identifier)
        del self.listeners[listener_identifier]

    # ---- Rules ----

    def create_rule(
        self,
        action: dict[str, Any],
        client_token: str,
        listener_identifier: str,
        match: dict[str, Any],
        name: str,
        priority: int,
        service_identifier: str,
        tags: dict[str, str],
    ) -> VPCLatticeRule:
        rule = VPCLatticeRule(
            self.region_name,
            self.account_id,
            action,
            client_token,
            listener_identifier,
            match,
            name,
            priority,
            service_identifier,
            tags,
        )
        self.rules[rule.id] = rule
        self.tag_resource(rule.arn, tags or {})
        return rule

    def get_rule(
        self,
        service_identifier: str,
        listener_identifier: str,
        rule_identifier: str,
    ) -> VPCLatticeRule:
        rule = self.rules.get(rule_identifier)
        if not rule:
            raise ResourceNotFoundException(rule_identifier)
        return rule

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_rules(
        self, service_identifier: str, listener_identifier: str
    ) -> list[VPCLatticeRule]:
        return [
            r for r in self.rules.values()
            if r.listener_identifier == listener_identifier
            and r.service_identifier == service_identifier
        ]

    def update_rule(
        self,
        service_identifier: str,
        listener_identifier: str,
        rule_identifier: str,
        action: Optional[dict[str, Any]],
        match: Optional[dict[str, Any]],
        priority: Optional[int],
    ) -> VPCLatticeRule:
        rule = self.get_rule(service_identifier, listener_identifier, rule_identifier)
        if action is not None:
            rule.action = action
        if match is not None:
            rule.match = match
        if priority is not None:
            rule.priority = priority
        return rule

    def delete_rule(
        self,
        service_identifier: str,
        listener_identifier: str,
        rule_identifier: str,
    ) -> None:
        self.get_rule(service_identifier, listener_identifier, rule_identifier)
        del self.rules[rule_identifier]

    def batch_update_rule(
        self,
        service_identifier: str,
        listener_identifier: str,
        rules: list[dict[str, Any]],
    ) -> dict[str, Any]:
        successful = []
        unsuccessful = []
        for rule_update in rules:
            rule_id = rule_update.get("ruleIdentifier", "")
            try:
                rule = self.get_rule(service_identifier, listener_identifier, rule_id)
                if "action" in rule_update:
                    rule.action = rule_update["action"]
                if "match" in rule_update:
                    rule.match = rule_update["match"]
                if "priority" in rule_update:
                    rule.priority = rule_update["priority"]
                successful.append(rule.to_dict())
            except ResourceNotFoundException:
                unsuccessful.append({"ruleIdentifier": rule_id})
        return {"successful": successful, "unsuccessful": unsuccessful}

    # ---- Target Groups ----

    def create_target_group(
        self,
        client_token: str,
        config: Optional[dict[str, Any]],
        name: str,
        tg_type: str,
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeTargetGroup:
        tg = VPCLatticeTargetGroup(
            self.region_name,
            self.account_id,
            client_token,
            config,
            name,
            tg_type,
            tags,
        )
        self.target_groups[tg.id] = tg
        self.tag_resource(tg.arn, tags or {})
        return tg

    def get_target_group(self, target_group_identifier: str) -> VPCLatticeTargetGroup:
        tg = self.target_groups.get(target_group_identifier)
        if not tg:
            # try by name or arn
            for t in self.target_groups.values():
                if t.name == target_group_identifier or t.arn == target_group_identifier:
                    return t
            raise ResourceNotFoundException(target_group_identifier)
        return tg

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_target_groups(
        self,
        target_group_type: Optional[str] = None,
        vpc_identifier: Optional[str] = None,
    ) -> list[VPCLatticeTargetGroup]:
        results = list(self.target_groups.values())
        if target_group_type:
            results = [tg for tg in results if tg.type == target_group_type]
        if vpc_identifier:
            results = [
                tg for tg in results
                if tg.config.get("vpcIdentifier") == vpc_identifier
            ]
        return results

    def update_target_group(
        self,
        target_group_identifier: str,
        health_check: dict[str, Any],
    ) -> VPCLatticeTargetGroup:
        tg = self.get_target_group(target_group_identifier)
        tg.config["healthCheck"] = health_check
        return tg

    def delete_target_group(self, target_group_identifier: str) -> VPCLatticeTargetGroup:
        tg = self.get_target_group(target_group_identifier)
        tg.status = "DELETE_IN_PROGRESS"
        del self.target_groups[tg.id]
        return tg

    def register_targets(
        self,
        target_group_identifier: str,
        targets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tg = self.get_target_group(target_group_identifier)
        successful = []
        unsuccessful = []
        for target in targets:
            tg.targets.append(target)
            successful.append(target)
        return {"successful": successful, "unsuccessful": unsuccessful}

    def deregister_targets(
        self,
        target_group_identifier: str,
        targets: list[dict[str, Any]],
    ) -> dict[str, Any]:
        tg = self.get_target_group(target_group_identifier)
        successful = []
        unsuccessful = []
        for target in targets:
            target_id = target.get("id")
            matching = [t for t in tg.targets if t.get("id") == target_id]
            if matching:
                tg.targets = [t for t in tg.targets if t.get("id") != target_id]
                successful.append(target)
            else:
                unsuccessful.append({"target": target, "failureCode": "TargetNotFound"})
        return {"successful": successful, "unsuccessful": unsuccessful}

    @paginate(pagination_model=PAGINATION_MODEL)
    def list_targets(
        self,
        target_group_identifier: str,
    ) -> list[dict[str, Any]]:
        tg = self.get_target_group(target_group_identifier)
        return [
            {**t, "id": t.get("id", ""), "port": t.get("port", 0), "status": "HEALTHY"}
            for t in tg.targets
        ]

    # ---- Tags ----

    def tag_resource(self, resource_arn: str, tags: dict[str, str]) -> None:
        tags_input = self.tagger.convert_dict_to_tags_input(tags or {})
        self.tagger.tag_resource(resource_arn, tags_input)

    def list_tags_for_resource(self, resource_arn: str) -> dict[str, str]:
        return self.tagger.get_tag_dict_for_resource(resource_arn)

    def untag_resource(self, resource_arn: str, tag_keys: list[str]) -> None:
        if not isinstance(tag_keys, list):
            tag_keys = [tag_keys]
        self.tagger.untag_resource_using_names(resource_arn, tag_keys)

    # ---- Access Log Subscriptions ----

    def create_access_log_subscription(
        self,
        resourceIdentifier: str,
        destinationArn: str,
        client_token: Optional[str],
        serviceNetworkLogType: Optional[str],
        tags: Optional[dict[str, str]],
    ) -> VPCLatticeAccessLogSubscription:
        resource: Any = None
        if resourceIdentifier.startswith("sn-"):
            resource = self.service_networks.get(resourceIdentifier)
        elif resourceIdentifier.startswith("svc-"):
            resource = self.services.get(resourceIdentifier)
        else:
            raise ValidationException(
                "Invalid parameter resourceIdentifier, must start with 'sn-' or 'svc-'"
            )

        if not resource:
            raise ResourceNotFoundException(f"Resource {resourceIdentifier} not found")

        sub = VPCLatticeAccessLogSubscription(
            self.region_name,
            self.account_id,
            destinationArn,
            resource.arn,
            resource.id,
            serviceNetworkLogType,
            tags,
        )

        self.access_log_subscriptions[sub.id] = sub
        return sub

    def get_access_log_subscription(
        self, accessLogSubscriptionIdentifier: str
    ) -> VPCLatticeAccessLogSubscription:
        sub = self.access_log_subscriptions.get(accessLogSubscriptionIdentifier)
        if not sub:
            raise ResourceNotFoundException(
                f"Access Log Subscription {accessLogSubscriptionIdentifier} not found"
            )
        return sub

    def list_access_log_subscriptions(
        self,
        resourceIdentifier: str,
        maxResults: Optional[int] = None,
        nextToken: Optional[str] = None,
    ) -> list[VPCLatticeAccessLogSubscription]:
        return [
            sub
            for sub in self.access_log_subscriptions.values()
            if sub.resourceId == resourceIdentifier
            or sub.resourceArn == resourceIdentifier
        ][:maxResults]

    def update_access_log_subscription(
        self,
        accessLogSubscriptionIdentifier: str,
        destinationArn: str,
    ) -> VPCLatticeAccessLogSubscription:
        sub = self.access_log_subscriptions.get(accessLogSubscriptionIdentifier)
        if not sub:
            raise ResourceNotFoundException(
                f"Access Log Subscription {accessLogSubscriptionIdentifier} not found"
            )

        sub.destinationArn = destinationArn
        sub.last_updated_at = datetime.now(timezone.utc).isoformat()

        return sub

    def delete_access_log_subscription(
        self, accessLogSubscriptionIdentifier: str
    ) -> None:
        sub = self.access_log_subscriptions.get(accessLogSubscriptionIdentifier)
        if not sub:
            raise ResourceNotFoundException(
                f"Access Log Subscription {accessLogSubscriptionIdentifier} not found"
            )
        del self.access_log_subscriptions[accessLogSubscriptionIdentifier]

    # ---- Auth Policies ----

    def put_auth_policy(self, resourceIdentifier: str, policy: str) -> AuthPolicy:
        # ResourceConfig not supported yet, only handle Service and Service Network
        if resourceIdentifier.startswith("arn:"):
            resourceIdentifier = resourceIdentifier.rsplit("/", 1)[-1]

        resource: Any = None

        if resourceIdentifier.startswith("sn-"):
            resource = self.service_networks.get(resourceIdentifier)
        elif resourceIdentifier.startswith("svc-"):
            resource = self.services.get(resourceIdentifier)
        else:
            raise ValidationException(
                "Invalid parameter resourceIdentifier, must start with 'sn-' or 'svc-'"
            )

        if not resource:
            raise ResourceNotFoundException(f"Resource {resourceIdentifier} not found")

        # Handle state management
        state = "Inactive" if resource.auth_type == "NONE" else "Active"

        now_iso = datetime.now(timezone.utc).isoformat()
        if resourceIdentifier in self.auth_policies:
            auth_policy = self.auth_policies[resourceIdentifier]
            auth_policy.policy = policy
            auth_policy.last_updated_at = now_iso
            auth_policy.state = state

        else:
            auth_policy = AuthPolicy(
                policy_name=resourceIdentifier,
                policy=policy,
                created_at=now_iso,
                last_updated_at=now_iso,
                state=state,
            )

            self.auth_policies[resourceIdentifier] = auth_policy

        return auth_policy

    def get_auth_policy(self, resourceIdentifier: str) -> AuthPolicy:
        original_identifier = resourceIdentifier
        if resourceIdentifier.startswith("arn:"):
            resourceIdentifier = resourceIdentifier.rsplit("/", 1)[-1]

        auth_policy = self.auth_policies.get(resourceIdentifier)
        if not auth_policy:
            raise ResourceNotFoundException(f"Resource {original_identifier} not found")

        resource: Any
        if resourceIdentifier.startswith("sn-"):
            resource = self.service_networks.get(resourceIdentifier)
        else:
            resource = self.services.get(resourceIdentifier)

        auth_policy.state = (
            "Inactive" if not resource or resource.auth_type == "NONE" else "Active"
        )

        return auth_policy

    def delete_auth_policy(self, resourceIdentifier: str) -> None:
        original_identifier = resourceIdentifier

        if resourceIdentifier.startswith("arn:"):
            resourceIdentifier = resourceIdentifier.rsplit("/", 1)[-1]

        if resourceIdentifier not in self.auth_policies:
            raise ResourceNotFoundException(f"Resource {original_identifier} not found")

        del self.auth_policies[resourceIdentifier]

    # ---- Resource Policies ----

    def put_resource_policy(self, resourceArn: str, policy: str) -> None:
        self.resource_policies[resourceArn] = policy

    def get_resource_policy(self, resourceArn: str) -> str:
        if resourceArn not in self.resource_policies:
            raise ResourceNotFoundException(f"Resource {resourceArn} not found")

        return self.resource_policies[resourceArn]

    def delete_resource_policy(self, resourceArn: str) -> None:
        if resourceArn not in self.resource_policies:
            raise ResourceNotFoundException(f"Resource {resourceArn} not found")

        del self.resource_policies[resourceArn]


vpclattice_backends: BackendDict[VPCLatticeBackend] = BackendDict(
    VPCLatticeBackend, "vpc-lattice"
)
