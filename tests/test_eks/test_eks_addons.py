import boto3
import pytest
from botocore.exceptions import ClientError

from moto import mock_aws

REGION = "us-east-1"
CLUSTER_NAME = "test-cluster"
ROLE_ARN = "arn:aws:iam::123456789012:role/eks-role"


def _create_cluster(client):
    client.create_cluster(
        name=CLUSTER_NAME,
        roleArn=ROLE_ARN,
        resourcesVpcConfig={"subnetIds": ["subnet-12345"], "securityGroupIds": ["sg-12345"]},
    )


# --- Addon CRUD Tests ---


@mock_aws
def test_create_addon():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    response = client.create_addon(
        clusterName=CLUSTER_NAME,
        addonName="vpc-cni",
        addonVersion="v1.12.0-eksbuild.1",
        serviceAccountRoleArn="arn:aws:iam::123456789012:role/addon-role",
        tags={"env": "test"},
    )

    addon = response["addon"]
    assert addon["addonName"] == "vpc-cni"
    assert addon["clusterName"] == CLUSTER_NAME
    assert addon["status"] == "ACTIVE"
    assert addon["addonVersion"] == "v1.12.0-eksbuild.1"
    assert addon["tags"] == {"env": "test"}
    assert "addonArn" in addon
    assert "createdAt" in addon


@mock_aws
def test_create_addon_duplicate():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    client.create_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")

    with pytest.raises(ClientError) as exc:
        client.create_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")
    assert exc.value.response["Error"]["Code"] == "ResourceInUseException"


@mock_aws
def test_create_addon_cluster_not_found():
    client = boto3.client("eks", region_name=REGION)

    with pytest.raises(ClientError) as exc:
        client.create_addon(clusterName="nonexistent", addonName="vpc-cni")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_describe_addon():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)
    client.create_addon(
        clusterName=CLUSTER_NAME,
        addonName="coredns",
        addonVersion="v1.9.3-eksbuild.2",
    )

    response = client.describe_addon(clusterName=CLUSTER_NAME, addonName="coredns")
    addon = response["addon"]
    assert addon["addonName"] == "coredns"
    assert addon["addonVersion"] == "v1.9.3-eksbuild.2"
    assert addon["status"] == "ACTIVE"


@mock_aws
def test_describe_addon_not_found():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    with pytest.raises(ClientError) as exc:
        client.describe_addon(clusterName=CLUSTER_NAME, addonName="nonexistent")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_addon():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)
    client.create_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")

    response = client.delete_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")
    assert response["addon"]["addonName"] == "vpc-cni"
    assert response["addon"]["status"] == "DELETING"

    # Verify it's gone
    with pytest.raises(ClientError) as exc:
        client.describe_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_addons():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    # Empty list
    response = client.list_addons(clusterName=CLUSTER_NAME)
    assert response["addons"] == []

    # Add some addons
    client.create_addon(clusterName=CLUSTER_NAME, addonName="vpc-cni")
    client.create_addon(clusterName=CLUSTER_NAME, addonName="coredns")
    client.create_addon(clusterName=CLUSTER_NAME, addonName="kube-proxy")

    response = client.list_addons(clusterName=CLUSTER_NAME)
    assert sorted(response["addons"]) == ["coredns", "kube-proxy", "vpc-cni"]


@mock_aws
def test_describe_addon_versions():
    client = boto3.client("eks", region_name=REGION)

    response = client.describe_addon_versions()
    addons = response["addons"]
    assert len(addons) > 0
    addon_names = [a["addonName"] for a in addons]
    assert "vpc-cni" in addon_names
    assert "coredns" in addon_names

    # Filter by addon name
    response = client.describe_addon_versions(addonName="vpc-cni")
    assert len(response["addons"]) == 1
    assert response["addons"][0]["addonName"] == "vpc-cni"


# --- Access Entry CRUD Tests ---


@mock_aws
def test_create_access_entry():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    principal_arn = "arn:aws:iam::123456789012:role/my-role"
    response = client.create_access_entry(
        clusterName=CLUSTER_NAME,
        principalArn=principal_arn,
        kubernetesGroups=["my-group"],
        tags={"env": "test"},
        type="STANDARD",
    )

    entry = response["accessEntry"]
    assert entry["clusterName"] == CLUSTER_NAME
    assert entry["principalArn"] == principal_arn
    assert entry["kubernetesGroups"] == ["my-group"]
    assert entry["tags"] == {"env": "test"}
    assert entry["type"] == "STANDARD"
    assert "accessEntryArn" in entry
    assert "createdAt" in entry


@mock_aws
def test_create_access_entry_duplicate():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    principal_arn = "arn:aws:iam::123456789012:role/my-role"
    client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)

    with pytest.raises(ClientError) as exc:
        client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)
    assert exc.value.response["Error"]["Code"] == "ResourceInUseException"


@mock_aws
def test_describe_access_entry():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    principal_arn = "arn:aws:iam::123456789012:role/my-role"
    client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)

    response = client.describe_access_entry(
        clusterName=CLUSTER_NAME, principalArn=principal_arn
    )
    entry = response["accessEntry"]
    assert entry["principalArn"] == principal_arn
    assert entry["clusterName"] == CLUSTER_NAME


@mock_aws
def test_describe_access_entry_not_found():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    with pytest.raises(ClientError) as exc:
        client.describe_access_entry(
            clusterName=CLUSTER_NAME,
            principalArn="arn:aws:iam::123456789012:role/nonexistent",
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_access_entry():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    principal_arn = "arn:aws:iam::123456789012:role/my-role"
    client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)

    client.delete_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)

    with pytest.raises(ClientError) as exc:
        client.describe_access_entry(
            clusterName=CLUSTER_NAME, principalArn=principal_arn
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_access_entries():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    response = client.list_access_entries(clusterName=CLUSTER_NAME)
    assert response["accessEntries"] == []

    arns = [
        "arn:aws:iam::123456789012:role/role-a",
        "arn:aws:iam::123456789012:role/role-b",
    ]
    for arn in arns:
        client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=arn)

    response = client.list_access_entries(clusterName=CLUSTER_NAME)
    assert sorted(response["accessEntries"]) == sorted(arns)


# --- Access Policy Tests ---


@mock_aws
def test_associate_and_disassociate_access_policy():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    principal_arn = "arn:aws:iam::123456789012:role/my-role"
    client.create_access_entry(clusterName=CLUSTER_NAME, principalArn=principal_arn)

    policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
    response = client.associate_access_policy(
        clusterName=CLUSTER_NAME,
        principalArn=principal_arn,
        policyArn=policy_arn,
        accessScope={"type": "cluster"},
    )

    assert response["clusterName"] == CLUSTER_NAME
    assert response["principalArn"] == principal_arn
    policy = response["associatedAccessPolicy"]
    assert policy["policyArn"] == policy_arn
    assert policy["accessScope"] == {"type": "cluster"}

    # Disassociate
    client.disassociate_access_policy(
        clusterName=CLUSTER_NAME,
        principalArn=principal_arn,
        policyArn=policy_arn,
    )

    # Disassociating again should fail
    with pytest.raises(ClientError) as exc:
        client.disassociate_access_policy(
            clusterName=CLUSTER_NAME,
            principalArn=principal_arn,
            policyArn=policy_arn,
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


# --- Pod Identity Association Tests ---


@mock_aws
def test_create_pod_identity_association():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    response = client.create_pod_identity_association(
        clusterName=CLUSTER_NAME,
        namespace="default",
        serviceAccount="my-sa",
        roleArn="arn:aws:iam::123456789012:role/pod-role",
        tags={"env": "test"},
    )

    assoc = response["association"]
    assert assoc["clusterName"] == CLUSTER_NAME
    assert assoc["namespace"] == "default"
    assert assoc["serviceAccount"] == "my-sa"
    assert assoc["roleArn"] == "arn:aws:iam::123456789012:role/pod-role"
    assert assoc["tags"] == {"env": "test"}
    assert "associationArn" in assoc
    assert "associationId" in assoc
    assert assoc["associationId"].startswith("a-")


@mock_aws
def test_describe_pod_identity_association():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    create_resp = client.create_pod_identity_association(
        clusterName=CLUSTER_NAME,
        namespace="default",
        serviceAccount="my-sa",
        roleArn="arn:aws:iam::123456789012:role/pod-role",
    )
    assoc_id = create_resp["association"]["associationId"]

    response = client.describe_pod_identity_association(
        clusterName=CLUSTER_NAME, associationId=assoc_id
    )
    assoc = response["association"]
    assert assoc["associationId"] == assoc_id
    assert assoc["namespace"] == "default"


@mock_aws
def test_describe_pod_identity_association_not_found():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    with pytest.raises(ClientError) as exc:
        client.describe_pod_identity_association(
            clusterName=CLUSTER_NAME, associationId="a-nonexistent"
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_delete_pod_identity_association():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    create_resp = client.create_pod_identity_association(
        clusterName=CLUSTER_NAME,
        namespace="default",
        serviceAccount="my-sa",
        roleArn="arn:aws:iam::123456789012:role/pod-role",
    )
    assoc_id = create_resp["association"]["associationId"]

    response = client.delete_pod_identity_association(
        clusterName=CLUSTER_NAME, associationId=assoc_id
    )
    assert response["association"]["associationId"] == assoc_id

    # Verify deletion
    with pytest.raises(ClientError) as exc:
        client.describe_pod_identity_association(
            clusterName=CLUSTER_NAME, associationId=assoc_id
        )
    assert exc.value.response["Error"]["Code"] == "ResourceNotFoundException"


@mock_aws
def test_list_pod_identity_associations():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)

    # Empty
    response = client.list_pod_identity_associations(clusterName=CLUSTER_NAME)
    assert response["associations"] == []

    # Create two
    client.create_pod_identity_association(
        clusterName=CLUSTER_NAME,
        namespace="default",
        serviceAccount="sa-1",
        roleArn="arn:aws:iam::123456789012:role/role-1",
    )
    client.create_pod_identity_association(
        clusterName=CLUSTER_NAME,
        namespace="kube-system",
        serviceAccount="sa-2",
        roleArn="arn:aws:iam::123456789012:role/role-2",
    )

    response = client.list_pod_identity_associations(clusterName=CLUSTER_NAME)
    assert len(response["associations"]) == 2

    # Filter by namespace
    response = client.list_pod_identity_associations(
        clusterName=CLUSTER_NAME, namespace="default"
    )
    assert len(response["associations"]) == 1
    assert response["associations"][0]["namespace"] == "default"


# --- Tagging Tests (extended) ---


@mock_aws
def test_tag_addon():
    client = boto3.client("eks", region_name=REGION)
    _create_cluster(client)
    create_resp = client.create_addon(
        clusterName=CLUSTER_NAME,
        addonName="vpc-cni",
        tags={"initial": "tag"},
    )
    addon_arn = create_resp["addon"]["addonArn"]

    # Tag it
    client.tag_resource(resourceArn=addon_arn, tags={"new": "tag"})

    # Verify
    tags = client.list_tags_for_resource(resourceArn=addon_arn)["tags"]
    assert tags == {"initial": "tag", "new": "tag"}

    # Untag
    client.untag_resource(resourceArn=addon_arn, tagKeys=["initial"])
    tags = client.list_tags_for_resource(resourceArn=addon_arn)["tags"]
    assert tags == {"new": "tag"}
