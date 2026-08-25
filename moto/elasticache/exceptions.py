from moto.core.exceptions import ServiceException


class ElastiCacheException(ServiceException):
    pass


class PasswordTooShort(ElastiCacheException):
    code = "InvalidParameterValue"
    message = "Passwords length must be between 16-128 characters."


class PasswordRequired(ElastiCacheException):
    code = "InvalidParameterValue"
    message = "No password was provided. If you want to create/update the user without password, please use the NoPasswordRequired flag."


class InvalidParameterValueException(ElastiCacheException):
    code = "InvalidParameterValue"


class InvalidParameterCombinationException(ElastiCacheException):
    code = "InvalidParameterCombination"


class UserAlreadyExists(ElastiCacheException):
    code = "UserAlreadyExists"

    def __init__(self) -> None:
        super().__init__("User user1 already exists.")


class UserNotFound(ElastiCacheException):
    code = "UserNotFound"

    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found.")


class CacheClusterAlreadyExists(ElastiCacheException):
    code = "CacheClusterAlreadyExists"

    def __init__(self, cache_cluster_id: str):
        super().__init__(f"Cache cluster {cache_cluster_id} already exists.")


class CacheClusterNotFound(ElastiCacheException):
    code = "CacheClusterNotFound"

    def __init__(self, cache_cluster_id: str):
        super().__init__(f"Cache cluster {cache_cluster_id} not found.")


class CacheSubnetGroupAlreadyExists(ElastiCacheException):
    code = "CacheSubnetGroupAlreadyExists"

    def __init__(self, cache_subnet_group_name: str):
        super().__init__(f"CacheSubnetGroup {cache_subnet_group_name} already exists.")


class CacheSubnetGroupNotFound(ElastiCacheException):
    code = "CacheSubnetGroupNotFoundFault"

    def __init__(self, cache_subnet_group_name: str):
        super().__init__(f"CacheSubnetGroup {cache_subnet_group_name} not found.")


class InvalidARNFault(ElastiCacheException):
    code = "InvalidARN"

    def __init__(self, arn: str):
        super().__init__(f"ARN {arn} is invalid.")


class InvalidSubnet(ElastiCacheException):
    code = "InvalidSubnet"

    def __init__(self, subnet_id: str):
        super().__init__(f"Subnet {subnet_id} is invalid.")


class ReplicationGroupAlreadyExists(ElastiCacheException):
    code = "ReplicationGroupAlreadyExists"

    def __init__(self, replication_group_id: str):
        super().__init__(f"Replication group {replication_group_id} already exists.")


class ReplicationGroupNotFound(ElastiCacheException):
    code = "ReplicationGroupNotFoundFault"

    def __init__(self, replication_group_id: str):
        super().__init__(f"Replication group {replication_group_id} not found.")


class SnapshotNotFound(ElastiCacheException):
    code = "SnapshotNotFoundFault"

    def __init__(self, snapshot_name: str):
        super().__init__(f"Snapshot {snapshot_name} not found.")


class SnapshotAlreadyExists(ElastiCacheException):
    code = "SnapshotAlreadyExistsFault"

    def __init__(self, snapshot_name: str):
        super().__init__(f"Snapshot {snapshot_name} already exists.")


class CacheParameterGroupAlreadyExists(ElastiCacheException):
    code = "CacheParameterGroupAlreadyExists"

    def __init__(self, name: str):
        super().__init__(f"Cache parameter group {name} already exists.")


class CacheParameterGroupNotFound(ElastiCacheException):
    code = "CacheParameterGroupNotFound"

    def __init__(self, name: str):
        super().__init__(f"Cache parameter group {name} not found.")


class CacheSecurityGroupAlreadyExists(ElastiCacheException):
    code = "CacheSecurityGroupAlreadyExists"

    def __init__(self, name: str):
        super().__init__(f"Cache security group {name} already exists.")


class CacheSecurityGroupNotFound(ElastiCacheException):
    code = "CacheSecurityGroupNotFound"

    def __init__(self, name: str):
        super().__init__(f"Cache security group {name} not found.")


class UserGroupAlreadyExists(ElastiCacheException):
    code = "UserGroupAlreadyExists"

    def __init__(self, user_group_id: str):
        super().__init__(f"User group {user_group_id} already exists.")


class UserGroupNotFound(ElastiCacheException):
    code = "UserGroupNotFoundFault"

    def __init__(self, user_group_id: str):
        super().__init__(f"User group {user_group_id} not found.")


class ServerlessCacheAlreadyExists(ElastiCacheException):
    code = "ServerlessCacheAlreadyExistsFault"

    def __init__(self, name: str):
        super().__init__(f"Serverless cache {name} already exists.")


class ServerlessCacheNotFound(ElastiCacheException):
    code = "ServerlessCacheNotFoundFault"

    def __init__(self, name: str):
        super().__init__(f"Serverless cache {name} not found.")


class GlobalReplicationGroupAlreadyExists(ElastiCacheException):
    code = "GlobalReplicationGroupAlreadyExistsFault"

    def __init__(self, name: str):
        super().__init__(f"Global replication group {name} already exists.")


class GlobalReplicationGroupNotFound(ElastiCacheException):
    code = "GlobalReplicationGroupNotFoundFault"

    def __init__(self, name: str):
        super().__init__(f"Global replication group {name} not found.")
