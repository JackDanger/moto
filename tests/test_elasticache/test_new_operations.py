"""Tests for newly implemented ElastiCache operations."""
import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws
from moto.core import DEFAULT_ACCOUNT_ID as ACCOUNT_ID


# ============================================================
# CacheParameterGroup tests
# ============================================================


@mock_aws
def test_create_cache_parameter_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    resp = client.create_cache_parameter_group(
        CacheParameterGroupName="my-param-group",
        CacheParameterGroupFamily="redis7",
        Description="Test parameter group",
    )
    group = resp["CacheParameterGroup"]
    assert group["CacheParameterGroupName"] == "my-param-group"
    assert group["CacheParameterGroupFamily"] == "redis7"
    assert group["Description"] == "Test parameter group"
    assert group["IsGlobal"] is False
    assert f"arn:aws:elasticache:us-east-1:{ACCOUNT_ID}:parametergroup:my-param-group" == group["ARN"]


@mock_aws
def test_create_cache_parameter_group_already_exists():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="my-param-group",
        CacheParameterGroupFamily="redis7",
        Description="Test",
    )
    with pytest.raises(ClientError) as exc:
        client.create_cache_parameter_group(
            CacheParameterGroupName="my-param-group",
            CacheParameterGroupFamily="redis7",
            Description="Test",
        )
    assert exc.value.response["Error"]["Code"] == "CacheParameterGroupAlreadyExists"


@mock_aws
def test_delete_cache_parameter_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="my-param-group",
        CacheParameterGroupFamily="redis7",
        Description="Test",
    )
    client.delete_cache_parameter_group(CacheParameterGroupName="my-param-group")
    # Verify it's gone (only defaults remain)
    resp = client.describe_cache_parameter_groups()
    names = [g["CacheParameterGroupName"] for g in resp["CacheParameterGroups"]]
    assert "my-param-group" not in names


@mock_aws
def test_delete_cache_parameter_group_not_found():
    client = boto3.client("elasticache", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_cache_parameter_group(CacheParameterGroupName="nonexistent")
    assert exc.value.response["Error"]["Code"] == "CacheParameterGroupNotFound"


@mock_aws
def test_describe_cache_parameter_groups_includes_custom():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="custom-pg",
        CacheParameterGroupFamily="redis6.x",
        Description="Custom group",
    )
    resp = client.describe_cache_parameter_groups()
    names = [g["CacheParameterGroupName"] for g in resp["CacheParameterGroups"]]
    assert "custom-pg" in names
    # Default groups should still be present
    assert "default.redis7" in names


@mock_aws
def test_describe_cache_parameter_groups_by_name():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="custom-pg",
        CacheParameterGroupFamily="redis7",
        Description="Custom group",
    )
    resp = client.describe_cache_parameter_groups(CacheParameterGroupName="custom-pg")
    assert len(resp["CacheParameterGroups"]) == 1
    assert resp["CacheParameterGroups"][0]["CacheParameterGroupName"] == "custom-pg"


@mock_aws
def test_modify_cache_parameter_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="my-pg",
        CacheParameterGroupFamily="redis7",
        Description="Test",
    )
    resp = client.modify_cache_parameter_group(
        CacheParameterGroupName="my-pg",
        ParameterNameValues=[
            {"ParameterName": "maxmemory-policy", "ParameterValue": "allkeys-lru"},
        ],
    )
    assert resp["CacheParameterGroupName"] == "my-pg"


@mock_aws
def test_reset_cache_parameter_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_parameter_group(
        CacheParameterGroupName="my-pg",
        CacheParameterGroupFamily="redis7",
        Description="Test",
    )
    client.modify_cache_parameter_group(
        CacheParameterGroupName="my-pg",
        ParameterNameValues=[
            {"ParameterName": "maxmemory-policy", "ParameterValue": "allkeys-lru"},
        ],
    )
    resp = client.reset_cache_parameter_group(
        CacheParameterGroupName="my-pg",
        ResetAllParameters=True,
    )
    assert resp["CacheParameterGroupName"] == "my-pg"


# ============================================================
# CacheSecurityGroup tests
# ============================================================


@mock_aws
def test_create_cache_security_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    resp = client.create_cache_security_group(
        CacheSecurityGroupName="my-sg",
        Description="Test security group",
    )
    group = resp["CacheSecurityGroup"]
    assert group["CacheSecurityGroupName"] == "my-sg"
    assert group["Description"] == "Test security group"
    assert group["OwnerId"] == ACCOUNT_ID


@mock_aws
def test_create_cache_security_group_already_exists():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_security_group(
        CacheSecurityGroupName="my-sg",
        Description="Test",
    )
    with pytest.raises(ClientError) as exc:
        client.create_cache_security_group(
            CacheSecurityGroupName="my-sg",
            Description="Test",
        )
    assert exc.value.response["Error"]["Code"] == "CacheSecurityGroupAlreadyExists"


@mock_aws
def test_delete_cache_security_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_security_group(
        CacheSecurityGroupName="my-sg",
        Description="Test",
    )
    client.delete_cache_security_group(CacheSecurityGroupName="my-sg")
    resp = client.describe_cache_security_groups()
    names = [g["CacheSecurityGroupName"] for g in resp["CacheSecurityGroups"]]
    assert "my-sg" not in names


@mock_aws
def test_delete_cache_security_group_not_found():
    client = boto3.client("elasticache", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_cache_security_group(CacheSecurityGroupName="nonexistent")
    assert exc.value.response["Error"]["Code"] == "CacheSecurityGroupNotFound"


@mock_aws
def test_describe_cache_security_groups():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_security_group(
        CacheSecurityGroupName="sg1",
        Description="First",
    )
    client.create_cache_security_group(
        CacheSecurityGroupName="sg2",
        Description="Second",
    )
    resp = client.describe_cache_security_groups()
    names = [g["CacheSecurityGroupName"] for g in resp["CacheSecurityGroups"]]
    assert "sg1" in names
    assert "sg2" in names


@mock_aws
def test_describe_cache_security_groups_by_name():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_security_group(
        CacheSecurityGroupName="sg1",
        Description="First",
    )
    resp = client.describe_cache_security_groups(CacheSecurityGroupName="sg1")
    assert len(resp["CacheSecurityGroups"]) == 1


@mock_aws
def test_revoke_cache_security_group_ingress():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_security_group(
        CacheSecurityGroupName="my-sg",
        Description="Test",
    )
    resp = client.revoke_cache_security_group_ingress(
        CacheSecurityGroupName="my-sg",
        EC2SecurityGroupName="ec2-sg",
        EC2SecurityGroupOwnerId=ACCOUNT_ID,
    )
    assert resp["CacheSecurityGroup"]["CacheSecurityGroupName"] == "my-sg"


# ============================================================
# UserGroup tests
# ============================================================


@mock_aws
def test_create_user_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    resp = client.create_user_group(
        UserGroupId="my-group",
        Engine="redis",
        UserIds=["default"],
    )
    assert resp["UserGroupId"] == "my-group"
    assert resp["Engine"] == "redis"
    assert resp["Status"] == "active"
    assert "default" in resp["UserIds"]
    assert f"arn:aws:elasticache:us-east-1:{ACCOUNT_ID}:usergroup:my-group" == resp["ARN"]


@mock_aws
def test_create_user_group_already_exists():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user_group(
        UserGroupId="my-group",
        Engine="redis",
        UserIds=["default"],
    )
    with pytest.raises(ClientError) as exc:
        client.create_user_group(
            UserGroupId="my-group",
            Engine="redis",
            UserIds=["default"],
        )
    assert exc.value.response["Error"]["Code"] == "UserGroupAlreadyExists"


@mock_aws
def test_delete_user_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user_group(
        UserGroupId="my-group",
        Engine="redis",
        UserIds=["default"],
    )
    resp = client.delete_user_group(UserGroupId="my-group")
    assert resp["UserGroupId"] == "my-group"
    assert resp["Status"] == "deleting"


@mock_aws
def test_delete_user_group_not_found():
    client = boto3.client("elasticache", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_user_group(UserGroupId="nonexistent")
    assert "UserGroupNotFound" in exc.value.response["Error"]["Code"]


@mock_aws
def test_describe_user_groups():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user_group(
        UserGroupId="group1",
        Engine="redis",
        UserIds=["default"],
    )
    resp = client.describe_user_groups()
    ids = [g["UserGroupId"] for g in resp["UserGroups"]]
    assert "group1" in ids


@mock_aws
def test_describe_user_groups_by_id():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user_group(
        UserGroupId="group1",
        Engine="redis",
        UserIds=["default"],
    )
    resp = client.describe_user_groups(UserGroupId="group1")
    assert len(resp["UserGroups"]) == 1
    assert resp["UserGroups"][0]["UserGroupId"] == "group1"


@mock_aws
def test_modify_user_group_add_user():
    client = boto3.client("elasticache", region_name="us-east-1")
    # Create a user first
    client.create_user(
        UserId="testuser",
        UserName="TestUser",
        Engine="redis",
        AccessString="on ~* +@all",
        NoPasswordRequired=True,
    )
    client.create_user_group(
        UserGroupId="my-group",
        Engine="redis",
        UserIds=["default"],
    )
    resp = client.modify_user_group(
        UserGroupId="my-group",
        UserIdsToAdd=["testuser"],
    )
    assert "testuser" in resp["UserIds"]


@mock_aws
def test_modify_user_group_remove_user():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user(
        UserId="testuser",
        UserName="TestUser",
        Engine="redis",
        AccessString="on ~* +@all",
        NoPasswordRequired=True,
    )
    client.create_user_group(
        UserGroupId="my-group",
        Engine="redis",
        UserIds=["default", "testuser"],
    )
    resp = client.modify_user_group(
        UserGroupId="my-group",
        UserIdsToRemove=["testuser"],
    )
    assert "testuser" not in resp["UserIds"]
    assert "default" in resp["UserIds"]


# ============================================================
# ServerlessCache tests
# ============================================================


@mock_aws
def test_create_serverless_cache():
    client = boto3.client("elasticache", region_name="us-east-1")
    resp = client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
        Description="Test cache",
    )
    cache = resp["ServerlessCache"]
    assert cache["ServerlessCacheName"] == "my-cache"
    assert cache["Engine"] == "redis"
    assert cache["Status"] == "available"
    assert "Endpoint" in cache


@mock_aws
def test_create_serverless_cache_already_exists():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
    )
    with pytest.raises(ClientError) as exc:
        client.create_serverless_cache(
            ServerlessCacheName="my-cache",
            Engine="redis",
        )
    assert exc.value.response["Error"]["Code"] == "ServerlessCacheAlreadyExistsFault"


@mock_aws
def test_delete_serverless_cache():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
    )
    resp = client.delete_serverless_cache(ServerlessCacheName="my-cache")
    cache = resp["ServerlessCache"]
    assert cache["ServerlessCacheName"] == "my-cache"
    assert cache["Status"] == "deleting"


@mock_aws
def test_delete_serverless_cache_not_found():
    client = boto3.client("elasticache", region_name="us-east-1")
    with pytest.raises(ClientError) as exc:
        client.delete_serverless_cache(ServerlessCacheName="nonexistent")
    assert exc.value.response["Error"]["Code"] == "ServerlessCacheNotFoundFault"


@mock_aws
def test_describe_serverless_caches():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="cache1",
        Engine="redis",
    )
    resp = client.describe_serverless_caches()
    names = [c["ServerlessCacheName"] for c in resp["ServerlessCaches"]]
    assert "cache1" in names


@mock_aws
def test_describe_serverless_caches_by_name():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="cache1",
        Engine="redis",
    )
    resp = client.describe_serverless_caches(ServerlessCacheName="cache1")
    assert len(resp["ServerlessCaches"]) == 1


@mock_aws
def test_modify_serverless_cache():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
        Description="Original",
    )
    resp = client.modify_serverless_cache(
        ServerlessCacheName="my-cache",
        Description="Updated",
    )
    cache = resp["ServerlessCache"]
    assert cache["Description"] == "Updated"


# ============================================================
# GlobalReplicationGroup tests
# ============================================================


@mock_aws
def test_create_global_replication_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    # Need a replication group first
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Test RG",
        Engine="redis",
    )
    resp = client.create_global_replication_group(
        GlobalReplicationGroupIdSuffix="my-global",
        PrimaryReplicationGroupId="my-rg",
        GlobalReplicationGroupDescription="Test global",
    )
    grg = resp["GlobalReplicationGroup"]
    assert grg["GlobalReplicationGroupId"] == "lstgl-my-global"
    assert grg["GlobalReplicationGroupDescription"] == "Test global"
    assert grg["Status"] == "available"


@mock_aws
def test_delete_global_replication_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Test RG",
        Engine="redis",
    )
    client.create_global_replication_group(
        GlobalReplicationGroupIdSuffix="my-global",
        PrimaryReplicationGroupId="my-rg",
    )
    resp = client.delete_global_replication_group(
        GlobalReplicationGroupId="lstgl-my-global",
        RetainPrimaryReplicationGroup=True,
    )
    grg = resp["GlobalReplicationGroup"]
    assert grg["Status"] == "deleting"


@mock_aws
def test_describe_global_replication_groups():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Test RG",
        Engine="redis",
    )
    client.create_global_replication_group(
        GlobalReplicationGroupIdSuffix="my-global",
        PrimaryReplicationGroupId="my-rg",
    )
    resp = client.describe_global_replication_groups()
    ids = [g["GlobalReplicationGroupId"] for g in resp["GlobalReplicationGroups"]]
    assert "lstgl-my-global" in ids


@mock_aws
def test_describe_global_replication_groups_by_id():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Test RG",
        Engine="redis",
    )
    client.create_global_replication_group(
        GlobalReplicationGroupIdSuffix="my-global",
        PrimaryReplicationGroupId="my-rg",
    )
    resp = client.describe_global_replication_groups(
        GlobalReplicationGroupId="lstgl-my-global",
    )
    assert len(resp["GlobalReplicationGroups"]) == 1


@mock_aws
def test_modify_global_replication_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Test RG",
        Engine="redis",
    )
    client.create_global_replication_group(
        GlobalReplicationGroupIdSuffix="my-global",
        PrimaryReplicationGroupId="my-rg",
    )
    resp = client.modify_global_replication_group(
        GlobalReplicationGroupId="lstgl-my-global",
        ApplyImmediately=True,
        GlobalReplicationGroupDescription="Updated description",
    )
    grg = resp["GlobalReplicationGroup"]
    assert grg["GlobalReplicationGroupDescription"] == "Updated description"


# ============================================================
# ModifyUser test
# ============================================================


@mock_aws
def test_modify_user():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_user(
        UserId="testuser",
        UserName="TestUser",
        Engine="redis",
        AccessString="on ~* +@all",
        NoPasswordRequired=True,
    )
    resp = client.modify_user(
        UserId="testuser",
        AccessString="on ~keys:* +@read",
    )
    assert resp["UserId"] == "testuser"
    assert resp["AccessString"] == "on ~keys:* +@read"


# ============================================================
# ModifyCacheCluster test
# ============================================================


@mock_aws
def test_modify_cache_cluster():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_cluster(
        CacheClusterId="my-cluster",
        CacheNodeType="cache.t3.micro",
        Engine="redis",
        NumCacheNodes=1,
    )
    resp = client.modify_cache_cluster(
        CacheClusterId="my-cluster",
        SnapshotRetentionLimit=5,
    )
    cluster = resp["CacheCluster"]
    assert cluster["CacheClusterId"] == "my-cluster"
    assert cluster["SnapshotRetentionLimit"] == 5


# ============================================================
# ModifyReplicationGroup test
# ============================================================


@mock_aws
def test_modify_replication_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Original",
        Engine="redis",
    )
    resp = client.modify_replication_group(
        ReplicationGroupId="my-rg",
        ReplicationGroupDescription="Updated",
    )
    rg = resp["ReplicationGroup"]
    assert rg["Description"] == "Updated"


# ============================================================
# ModifyCacheSubnetGroup test
# ============================================================


@mock_aws
def test_modify_cache_subnet_group():
    client = boto3.client("elasticache", region_name="us-east-1")
    ec2 = boto3.resource("ec2", region_name="us-east-1")
    vpc = ec2.create_vpc(CidrBlock="10.0.0.0/16")
    subnet = ec2.create_subnet(VpcId=vpc.id, CidrBlock="10.0.1.0/24")
    client.create_cache_subnet_group(
        CacheSubnetGroupName="my-subnet-group",
        CacheSubnetGroupDescription="Original",
        SubnetIds=[subnet.id],
    )
    resp = client.modify_cache_subnet_group(
        CacheSubnetGroupName="my-subnet-group",
        CacheSubnetGroupDescription="Updated",
    )
    group = resp["CacheSubnetGroup"]
    assert group["CacheSubnetGroupDescription"] == "Updated"


# ============================================================
# CopySnapshot test
# ============================================================


@mock_aws
def test_copy_snapshot():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_cache_cluster(
        CacheClusterId="my-cluster",
        CacheNodeType="cache.t3.micro",
        Engine="redis",
        NumCacheNodes=1,
    )
    client.create_snapshot(
        SnapshotName="source-snap",
        CacheClusterId="my-cluster",
    )
    resp = client.copy_snapshot(
        SourceSnapshotName="source-snap",
        TargetSnapshotName="target-snap",
    )
    snap = resp["Snapshot"]
    assert snap["SnapshotName"] == "target-snap"
    assert snap["SnapshotStatus"] == "available"


# ============================================================
# ServerlessCacheSnapshot tests
# ============================================================


@mock_aws
def test_create_serverless_cache_snapshot():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
    )
    resp = client.create_serverless_cache_snapshot(
        ServerlessCacheSnapshotName="my-snap",
        ServerlessCacheName="my-cache",
    )
    snap = resp["ServerlessCacheSnapshot"]
    assert snap["ServerlessCacheSnapshotName"] == "my-snap"
    assert snap["ServerlessCacheConfiguration"]["ServerlessCacheName"] == "my-cache"


@mock_aws
def test_delete_serverless_cache_snapshot():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
    )
    client.create_serverless_cache_snapshot(
        ServerlessCacheSnapshotName="my-snap",
        ServerlessCacheName="my-cache",
    )
    resp = client.delete_serverless_cache_snapshot(
        ServerlessCacheSnapshotName="my-snap",
    )
    snap = resp["ServerlessCacheSnapshot"]
    assert snap["Status"] == "deleting"


@mock_aws
def test_describe_serverless_cache_snapshots():
    client = boto3.client("elasticache", region_name="us-east-1")
    client.create_serverless_cache(
        ServerlessCacheName="my-cache",
        Engine="redis",
    )
    client.create_serverless_cache_snapshot(
        ServerlessCacheSnapshotName="snap1",
        ServerlessCacheName="my-cache",
    )
    resp = client.describe_serverless_cache_snapshots()
    names = [s["ServerlessCacheSnapshotName"] for s in resp["ServerlessCacheSnapshots"]]
    assert "snap1" in names
