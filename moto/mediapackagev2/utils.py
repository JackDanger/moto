PAGINATION_MODEL = {
    "list_channel_groups": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10000,
        "unique_attribute": "arn",
    },
    "list_channels": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10000,
        "unique_attribute": "arn",
    },
    "list_origin_endpoints": {
        "input_token": "next_token",
        "limit_key": "max_results",
        "limit_default": 10000,
        "unique_attribute": "arn",
    },
}
