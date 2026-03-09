compatible_versions = [
    {
        "SourceVersion": "Elasticsearch_7.7",
        "TargetVersions": [
            "Elasticsearch_7.8",
            "Elasticsearch_7.9",
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_6.8",
        "TargetVersions": [
            "Elasticsearch_7.1",
            "Elasticsearch_7.4",
            "Elasticsearch_7.7",
            "Elasticsearch_7.8",
            "Elasticsearch_7.9",
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_7.8",
        "TargetVersions": [
            "Elasticsearch_7.9",
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_7.9",
        "TargetVersions": [
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_7.10",
        "TargetVersions": [
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {"SourceVersion": "OpenSearch_2.3", "TargetVersions": ["OpenSearch_2.5"]},
    {
        "SourceVersion": "OpenSearch_1.0",
        "TargetVersions": ["OpenSearch_1.1", "OpenSearch_1.2", "OpenSearch_1.3"],
    },
    {
        "SourceVersion": "OpenSearch_1.1",
        "TargetVersions": ["OpenSearch_1.2", "OpenSearch_1.3"],
    },
    {"SourceVersion": "OpenSearch_1.2", "TargetVersions": ["OpenSearch_1.3"]},
    {
        "SourceVersion": "OpenSearch_1.3",
        "TargetVersions": ["OpenSearch_2.3", "OpenSearch_2.5"],
    },
    {
        "SourceVersion": "Elasticsearch_6.0",
        "TargetVersions": [
            "Elasticsearch_6.3",
            "Elasticsearch_6.4",
            "Elasticsearch_6.5",
            "Elasticsearch_6.7",
            "Elasticsearch_6.8",
        ],
    },
    {"SourceVersion": "Elasticsearch_5.1", "TargetVersions": ["Elasticsearch_5.6"]},
    {
        "SourceVersion": "Elasticsearch_7.1",
        "TargetVersions": [
            "Elasticsearch_7.4",
            "Elasticsearch_7.7",
            "Elasticsearch_7.8",
            "Elasticsearch_7.9",
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_6.2",
        "TargetVersions": [
            "Elasticsearch_6.3",
            "Elasticsearch_6.4",
            "Elasticsearch_6.5",
            "Elasticsearch_6.7",
            "Elasticsearch_6.8",
        ],
    },
    {"SourceVersion": "Elasticsearch_5.3", "TargetVersions": ["Elasticsearch_5.6"]},
    {
        "SourceVersion": "Elasticsearch_6.3",
        "TargetVersions": [
            "Elasticsearch_6.4",
            "Elasticsearch_6.5",
            "Elasticsearch_6.7",
            "Elasticsearch_6.8",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_6.4",
        "TargetVersions": [
            "Elasticsearch_6.5",
            "Elasticsearch_6.7",
            "Elasticsearch_6.8",
        ],
    },
    {"SourceVersion": "Elasticsearch_5.5", "TargetVersions": ["Elasticsearch_5.6"]},
    {
        "SourceVersion": "Elasticsearch_7.4",
        "TargetVersions": [
            "Elasticsearch_7.7",
            "Elasticsearch_7.8",
            "Elasticsearch_7.9",
            "Elasticsearch_7.10",
            "OpenSearch_1.0",
            "OpenSearch_1.1",
            "OpenSearch_1.2",
            "OpenSearch_1.3",
        ],
    },
    {
        "SourceVersion": "Elasticsearch_6.5",
        "TargetVersions": ["Elasticsearch_6.7", "Elasticsearch_6.8"],
    },
    {
        "SourceVersion": "Elasticsearch_5.6",
        "TargetVersions": [
            "Elasticsearch_6.3",
            "Elasticsearch_6.4",
            "Elasticsearch_6.5",
            "Elasticsearch_6.7",
            "Elasticsearch_6.8",
        ],
    },
    {"SourceVersion": "Elasticsearch_6.7", "TargetVersions": ["Elasticsearch_6.8"]},
]


opensearch_versions = [
    'OpenSearch_2.13', 'OpenSearch_2.11', 'OpenSearch_2.9', 'OpenSearch_2.7',
    'OpenSearch_2.5', 'OpenSearch_2.3', 'OpenSearch_1.3', 'OpenSearch_1.2',
    'OpenSearch_1.1', 'OpenSearch_1.0',
]

elasticsearch_versions = [
    'Elasticsearch_7.10', 'Elasticsearch_7.9', 'Elasticsearch_7.8',
    'Elasticsearch_7.7', 'Elasticsearch_7.4', 'Elasticsearch_7.1',
    'Elasticsearch_6.8', 'Elasticsearch_6.7', 'Elasticsearch_6.5',
    'Elasticsearch_6.4', 'Elasticsearch_6.3', 'Elasticsearch_6.2',
    'Elasticsearch_6.0', 'Elasticsearch_5.6', 'Elasticsearch_5.5',
    'Elasticsearch_5.3', 'Elasticsearch_5.1',
]

opensearch_instance_types = [
    {
        'InstanceType': 't3.small.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': True,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': False,
        'InstanceRole': ['data'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
    {
        'InstanceType': 't3.medium.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': True,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': False,
        'InstanceRole': ['data'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
    {
        'InstanceType': 'm5.large.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': True,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': False,
        'InstanceRole': ['data'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
    {
        'InstanceType': 'r5.large.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': True,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': True,
        'InstanceRole': ['data'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
    {
        'InstanceType': 'c5.large.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': True,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': False,
        'InstanceRole': ['data'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
    {
        'InstanceType': 'ultrawarm1.medium.search',
        'EncryptionEnabled': True,
        'CognitoEnabled': False,
        'AppLogsEnabled': True,
        'AdvancedSecurityEnabled': True,
        'WarmEnabled': True,
        'InstanceRole': ['warm'],
        'AvailabilityZones': ['us-east-1a', 'us-east-1b', 'us-east-1c'],
    },
]

elasticsearch_instance_types = [
    't2.small.elasticsearch',
    't2.medium.elasticsearch',
    'm4.large.elasticsearch',
    'm5.large.elasticsearch',
    'r4.large.elasticsearch',
    'r5.large.elasticsearch',
    'c4.large.elasticsearch',
    'c5.large.elasticsearch',
]

reserved_instance_offerings = [
    {
        'ReservedInstanceOfferingId': '00000001-0000-0000-0000-000000000001',
        'InstanceType': 't3.small.search',
        'Duration': 31536000,
        'FixedPrice': 500.0,
        'UsagePrice': 0.0,
        'CurrencyCode': 'USD',
        'PaymentOption': 'ALL_UPFRONT',
        'RecurringCharges': [],
    },
    {
        'ReservedInstanceOfferingId': '00000002-0000-0000-0000-000000000002',
        'InstanceType': 'm5.large.search',
        'Duration': 31536000,
        'FixedPrice': 2000.0,
        'UsagePrice': 0.0,
        'CurrencyCode': 'USD',
        'PaymentOption': 'ALL_UPFRONT',
        'RecurringCharges': [],
    },
    {
        'ReservedInstanceOfferingId': '00000003-0000-0000-0000-000000000003',
        'InstanceType': 'r5.large.search',
        'Duration': 94608000,
        'FixedPrice': 4500.0,
        'UsagePrice': 0.0,
        'CurrencyCode': 'USD',
        'PaymentOption': 'ALL_UPFRONT',
        'RecurringCharges': [],
    },
    {
        'ReservedInstanceOfferingId': '00000004-0000-0000-0000-000000000004',
        'InstanceType': 't3.medium.search',
        'Duration': 31536000,
        'FixedPrice': 0.0,
        'UsagePrice': 0.05,
        'CurrencyCode': 'USD',
        'PaymentOption': 'NO_UPFRONT',
        'RecurringCharges': [
            {'RecurringChargeAmount': 0.05, 'RecurringChargeFrequency': 'Hourly'}
        ],
    },
]
