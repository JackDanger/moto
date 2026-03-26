import json
from urllib.parse import unquote

from moto.core.responses import BaseResponse

from .models import VPCLatticeBackend, vpclattice_backends


class VPCLatticeResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="vpc-lattice")

    @property
    def backend(self) -> VPCLatticeBackend:
        return vpclattice_backends[self.current_account][self.region]

    # ---- Services ----

    def create_service(self) -> str:
        service = self.backend.create_service(
            auth_type=self._get_param("authType") or "NONE",
            certificate_arn=self._get_param("certificateArn"),
            client_token=self._get_param("clientToken") or "",
            custom_domain_name=self._get_param("customDomainName"),
            name=self._get_param("name"),
            tags=self._get_param("tags"),
        )
        return json.dumps(service.to_dict())

    def get_service(self) -> str:
        path = unquote(self.path)
        service = self.backend.get_service(service_identifier=path.split("/")[-1])
        return json.dumps(service.to_dict())

    def delete_service(self) -> str:
        path = unquote(self.path)
        service = self.backend.delete_service(service_identifier=path.split("/")[-1])
        result = service.to_dict()
        result["status"] = "DELETE_IN_PROGRESS"
        return json.dumps(result)

    def update_service(self) -> str:
        path = unquote(self.path)
        service_identifier = path.split("/")[-1]
        service = self.backend.update_service(
            service_identifier=service_identifier,
            auth_type=self._get_param("authType"),
            certificate_arn=self._get_param("certificateArn"),
        )
        return json.dumps(service.to_dict())

    def list_services(self) -> str:
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        services, next_token = self.backend.list_services(
            max_results=max_results, next_token=next_token
        )
        response = {
            "items": [service.to_dict() for service in services],
            "nextToken": next_token,
        }
        return json.dumps(response)

    # ---- Service Networks ----

    def create_service_network(self) -> str:
        sn = self.backend.create_service_network(
            auth_type=self._get_param("authType") or "NONE",
            client_token=self._get_param("clientToken") or "",
            name=self._get_param("name"),
            sharing_config=self._get_param("sharingConfig"),
            tags=self._get_param("tags"),
        )
        return json.dumps(sn.to_dict())

    def get_service_network(self) -> str:
        path = unquote(self.path)
        service_network = self.backend.get_service_network(
            service_network_identifier=path.split("/")[-1]
        )
        return json.dumps(service_network.to_dict())

    def delete_service_network(self) -> str:
        path = unquote(self.path)
        self.backend.delete_service_network(
            service_network_identifier=path.split("/")[-1]
        )
        return json.dumps({})

    def update_service_network(self) -> str:
        path = unquote(self.path)
        sn = self.backend.update_service_network(
            service_network_identifier=path.split("/")[-1],
            auth_type=self._get_param("authType") or "NONE",
        )
        return json.dumps(sn.to_dict())

    def list_service_networks(self) -> str:
        max_results = self._get_param("MaxResults")
        next_token = self._get_param("NextToken")
        service_networks, next_token = self.backend.list_service_networks(
            max_results=max_results, next_token=next_token
        )
        response = {
            "items": [
                service_network.to_dict() for service_network in service_networks
            ],
            "nextToken": next_token,
        }
        return json.dumps(response)

    # ---- Service Network VPC Associations ----

    def create_service_network_vpc_association(self) -> str:
        assoc = self.backend.create_service_network_vpc_association(
            client_token=self._get_param("clientToken") or "",
            security_group_ids=self._get_param("securityGroupIds"),
            service_network_identifier=self._get_param("serviceNetworkIdentifier"),
            tags=self._get_param("tags"),
            vpc_identifier=self._get_param("vpcIdentifier"),
        )
        return json.dumps(assoc.to_dict())

    def get_service_network_vpc_association(self) -> str:
        path = unquote(self.path)
        assoc = self.backend.get_service_network_vpc_association(
            service_network_vpc_association_identifier=path.split("/")[-1]
        )
        return json.dumps(assoc.to_dict())

    def list_service_network_vpc_associations(self) -> str:
        service_network_identifier = self._get_param("serviceNetworkIdentifier")
        vpc_identifier = self._get_param("vpcIdentifier")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        assocs, next_token = self.backend.list_service_network_vpc_associations(
            service_network_identifier=service_network_identifier,
            vpc_identifier=vpc_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": [a.to_dict() for a in assocs], "nextToken": next_token})

    def update_service_network_vpc_association(self) -> str:
        path = unquote(self.path)
        assoc = self.backend.update_service_network_vpc_association(
            service_network_vpc_association_identifier=path.split("/")[-1],
            security_group_ids=self._get_param("securityGroupIds") or [],
        )
        return json.dumps(assoc.to_dict())

    def delete_service_network_vpc_association(self) -> str:
        path = unquote(self.path)
        assoc = self.backend.delete_service_network_vpc_association(
            service_network_vpc_association_identifier=path.split("/")[-1]
        )
        return json.dumps(assoc.to_dict())

    # ---- Service Network Service Associations ----

    def create_service_network_service_association(self) -> str:
        assoc = self.backend.create_service_network_service_association(
            client_token=self._get_param("clientToken") or "",
            service_identifier=self._get_param("serviceIdentifier"),
            service_network_identifier=self._get_param("serviceNetworkIdentifier"),
            tags=self._get_param("tags"),
        )
        return json.dumps(assoc.to_dict())

    def get_service_network_service_association(self) -> str:
        path = unquote(self.path)
        assoc = self.backend.get_service_network_service_association(
            service_network_service_association_identifier=path.split("/")[-1]
        )
        return json.dumps(assoc.to_dict())

    def list_service_network_service_associations(self) -> str:
        service_network_identifier = self._get_param("serviceNetworkIdentifier")
        service_identifier = self._get_param("serviceIdentifier")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        assocs, next_token = self.backend.list_service_network_service_associations(
            service_network_identifier=service_network_identifier,
            service_identifier=service_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": [a.to_dict() for a in assocs], "nextToken": next_token})

    def delete_service_network_service_association(self) -> str:
        path = unquote(self.path)
        assoc = self.backend.delete_service_network_service_association(
            service_network_service_association_identifier=path.split("/")[-1]
        )
        result = assoc.to_dict()
        result["status"] = "DELETE_IN_PROGRESS"
        return json.dumps(result)

    # ---- Listeners ----

    def create_listener(self) -> str:
        path = unquote(self.path)
        # path: /services/{serviceIdentifier}/listeners
        parts = path.split("/")
        service_identifier = parts[-2]
        listener = self.backend.create_listener(
            client_token=self._get_param("clientToken") or "",
            default_action=self._get_param("defaultAction") or {},
            name=self._get_param("name"),
            port=self._get_param("port"),
            protocol=self._get_param("protocol"),
            service_identifier=service_identifier,
            tags=self._get_param("tags"),
        )
        return json.dumps(listener.to_dict())

    def get_listener(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners/{listenerIdentifier}
        listener_identifier = parts[-1]
        service_identifier = parts[-3]
        listener = self.backend.get_listener(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
        )
        return json.dumps(listener.to_dict())

    def list_listeners(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners
        service_identifier = parts[-2]
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        listeners, next_token = self.backend.list_listeners(
            service_identifier=service_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": [l.to_dict() for l in listeners], "nextToken": next_token})

    def update_listener(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        listener_identifier = parts[-1]
        service_identifier = parts[-3]
        listener = self.backend.update_listener(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            default_action=self._get_param("defaultAction") or {},
        )
        return json.dumps(listener.to_dict())

    def delete_listener(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        listener_identifier = parts[-1]
        service_identifier = parts[-3]
        self.backend.delete_listener(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
        )
        return json.dumps({})

    # ---- Rules ----

    def create_rule(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners/{listenerIdentifier}/rules
        listener_identifier = parts[-2]
        service_identifier = parts[-4]
        rule = self.backend.create_rule(
            action=self._get_param("action"),
            client_token=self._get_param("clientToken") or "",
            listener_identifier=listener_identifier,
            match=self._get_param("match"),
            name=self._get_param("name"),
            priority=self._get_param("priority"),
            service_identifier=service_identifier,
            tags=self._get_param("tags") or {},
        )
        return json.dumps(rule.to_dict())

    def get_rule(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners/{listenerIdentifier}/rules/{ruleIdentifier}
        rule_identifier = parts[-1]
        listener_identifier = parts[-3]
        service_identifier = parts[-5]
        rule = self.backend.get_rule(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            rule_identifier=rule_identifier,
        )
        return json.dumps(rule.to_dict())

    def list_rules(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners/{listenerIdentifier}/rules
        listener_identifier = parts[-2]
        service_identifier = parts[-4]
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        rules, next_token = self.backend.list_rules(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": [r.to_dict() for r in rules], "nextToken": next_token})

    def update_rule(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        rule_identifier = parts[-1]
        listener_identifier = parts[-3]
        service_identifier = parts[-5]
        rule = self.backend.update_rule(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            rule_identifier=rule_identifier,
            action=self._get_param("action"),
            match=self._get_param("match"),
            priority=self._get_param("priority"),
        )
        return json.dumps(rule.to_dict())

    def delete_rule(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        rule_identifier = parts[-1]
        listener_identifier = parts[-3]
        service_identifier = parts[-5]
        self.backend.delete_rule(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            rule_identifier=rule_identifier,
        )
        return json.dumps({})

    def batch_update_rule(self) -> str:
        path = unquote(self.path)
        parts = path.split("/")
        # /services/{serviceIdentifier}/listeners/{listenerIdentifier}/rules
        listener_identifier = parts[-2]
        service_identifier = parts[-4]
        rules = self._get_param("rules") or []
        result = self.backend.batch_update_rule(
            service_identifier=service_identifier,
            listener_identifier=listener_identifier,
            rules=rules,
        )
        return json.dumps(result)

    # ---- Target Groups ----

    def create_target_group(self) -> str:
        tg = self.backend.create_target_group(
            client_token=self._get_param("clientToken") or "",
            config=self._get_param("config"),
            name=self._get_param("name"),
            tg_type=self._get_param("type"),
            tags=self._get_param("tags"),
        )
        return json.dumps(tg.to_dict())

    def get_target_group(self) -> str:
        path = unquote(self.path)
        tg = self.backend.get_target_group(
            target_group_identifier=path.split("/")[-1]
        )
        return json.dumps(tg.to_dict())

    def list_target_groups(self) -> str:
        target_group_type = self._get_param("targetGroupType")
        vpc_identifier = self._get_param("vpcIdentifier")
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        tgs, next_token = self.backend.list_target_groups(
            target_group_type=target_group_type,
            vpc_identifier=vpc_identifier,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": [tg.to_dict() for tg in tgs], "nextToken": next_token})

    def update_target_group(self) -> str:
        path = unquote(self.path)
        tg = self.backend.update_target_group(
            target_group_identifier=path.split("/")[-1],
            health_check=self._get_param("healthCheck") or {},
        )
        return json.dumps(tg.to_dict())

    def delete_target_group(self) -> str:
        path = unquote(self.path)
        tg = self.backend.delete_target_group(
            target_group_identifier=path.split("/")[-1]
        )
        return json.dumps(tg.to_dict())

    def register_targets(self) -> str:
        path = unquote(self.path)
        # /targetgroups/{targetGroupIdentifier}/registertargets
        tg_id = path.split("/")[-2]
        result = self.backend.register_targets(
            target_group_identifier=tg_id,
            targets=self._get_param("targets") or [],
        )
        return json.dumps(result)

    def deregister_targets(self) -> str:
        path = unquote(self.path)
        # /targetgroups/{targetGroupIdentifier}/deregistertargets
        tg_id = path.split("/")[-2]
        result = self.backend.deregister_targets(
            target_group_identifier=tg_id,
            targets=self._get_param("targets") or [],
        )
        return json.dumps(result)

    def list_targets(self) -> str:
        path = unquote(self.path)
        # /targetgroups/{targetGroupIdentifier}/listtargets
        tg_id = path.split("/")[-2]
        max_results = self._get_param("maxResults")
        next_token = self._get_param("nextToken")
        targets, next_token = self.backend.list_targets(
            target_group_identifier=tg_id,
            max_results=max_results,
            next_token=next_token,
        )
        return json.dumps({"items": targets, "nextToken": next_token})

    # ---- Tags ----

    def list_tags_for_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tags = self.backend.list_tags_for_resource(resource_arn)
        return json.dumps({"tags": tags})

    def tag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tags = self._get_param("tags")
        self.backend.tag_resource(resource_arn, tags)
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        tag_keys = self._get_param("tagKeys")
        self.backend.untag_resource(resource_arn=resource_arn, tag_keys=tag_keys)
        return json.dumps({})

    # ---- Access Log Subscriptions ----

    def create_access_log_subscription(self) -> str:
        sub = self.backend.create_access_log_subscription(
            resourceIdentifier=self._get_param("resourceIdentifier"),
            destinationArn=self._get_param("destinationArn"),
            client_token=self._get_param("clientToken"),
            serviceNetworkLogType=self._get_param("serviceNetworkLogType"),
            tags=self._get_param("tags"),
        )

        return json.dumps(sub.to_dict())

    def get_access_log_subscription(self) -> str:
        path = unquote(self.path)

        sub = self.backend.get_access_log_subscription(
            accessLogSubscriptionIdentifier=path.split("/")[-1]
        )

        return json.dumps(sub.to_dict())

    def list_access_log_subscriptions(self) -> str:
        subs = self.backend.list_access_log_subscriptions(
            resourceIdentifier=self._get_param("resourceIdentifier"),
            maxResults=self._get_int_param("maxResults"),
            nextToken=self._get_param("nextToken"),
        )

        return json.dumps({"items": [s.to_dict() for s in subs], "nextToken": ""})

    def update_access_log_subscription(self) -> str:
        path = unquote(self.path)

        sub = self.backend.update_access_log_subscription(
            accessLogSubscriptionIdentifier=path.split("/")[-1],
            destinationArn=self._get_param("destinationArn"),
        )

        return json.dumps(sub.to_dict())

    def delete_access_log_subscription(self) -> str:
        path = unquote(self.path)

        self.backend.delete_access_log_subscription(
            accessLogSubscriptionIdentifier=path.split("/")[-1]
        )

        return json.dumps({})

    # ---- Auth Policies ----

    def put_auth_policy(self) -> str:
        resourceId = unquote(self._get_param("resourceIdentifier"))
        policy = self._get_param("policy")

        auth_policy = self.backend.put_auth_policy(
            resourceIdentifier=resourceId,
            policy=policy,
        )

        response = {
            "policy": auth_policy.policy,
            "state": auth_policy.state,
        }
        return json.dumps(response)

    def get_auth_policy(self) -> str:
        resourceId = unquote(self._get_param("resourceIdentifier"))
        auth_policy = self.backend.get_auth_policy(resourceIdentifier=resourceId)

        response = {
            "policy": auth_policy.policy,
            "state": auth_policy.state,
            "createdAt": auth_policy.created_at,
            "lastUpdatedAt": auth_policy.last_updated_at,
        }
        return json.dumps(response)

    def delete_auth_policy(self) -> str:
        resourceId = unquote(self._get_param("resourceIdentifier"))

        self.backend.delete_auth_policy(resourceIdentifier=resourceId)

        return "{}"

    # ---- Resource Policies ----

    def put_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))
        policy = self._get_param("policy")
        self.backend.put_resource_policy(
            resourceArn=resource_arn,
            policy=policy,
        )

        return "{}"

    def get_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))

        resource_policy = self.backend.get_resource_policy(resourceArn=resource_arn)

        return json.dumps({"policy": resource_policy})

    def delete_resource_policy(self) -> str:
        resource_arn = unquote(self._get_param("resourceArn"))

        self.backend.delete_resource_policy(resourceArn=resource_arn)

        return "{}"
