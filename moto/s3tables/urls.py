"""s3tables base URL and path."""

from .responses import S3TablesResponse

url_bases = [
    r"https?://s3tables\.(.+)\.amazonaws\.com",
]

url_paths = {
    # Table buckets
    "{0}/buckets$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/policy$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/maintenance/(?P<type>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/maintenance$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/encryption$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/metrics$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)/storage-class$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN>.+)$": S3TablesResponse.dispatch,
    "{0}/buckets/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)$": S3TablesResponse.dispatch,
    # Get table (query params)
    "{0}/get-table$": S3TablesResponse.dispatch,
    # Namespaces
    "{0}/namespaces/(?P<tableBucketARN>.+)$": S3TablesResponse.dispatch,
    # Tables with sub-resources
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/policy$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/policy$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance/(?P<type>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance/(?P<type>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance-job-status$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/maintenance-job-status$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/encryption$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/encryption$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/storage-class$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/storage-class$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/metadata-location$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/metadata-location$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/rename$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)/rename$": S3TablesResponse.dispatch,
    # Tables (CRUD)
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)/(?P<namespace>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN>[^/]+)$": S3TablesResponse.dispatch,
    "{0}/tables/(?P<tableBucketARN_pt_1>[^/]+)/(?P<tableBucketARN_pt_2>[^/]+)/(?P<namespace>[^/]+)/(?P<name>[^/]+)$": S3TablesResponse.dispatch,
    # Replication (query-param based)
    "{0}/table-bucket-replication$": S3TablesResponse.dispatch,
    "{0}/table-replication$": S3TablesResponse.dispatch,
    "{0}/replication-status$": S3TablesResponse.dispatch,
    # Record expiration (query-param based)
    "{0}/table-record-expiration$": S3TablesResponse.dispatch,
    "{0}/table-record-expiration-job-status$": S3TablesResponse.dispatch,
    # Tagging
    "{0}/tag/(?P<resourceArn>.+)$": S3TablesResponse.dispatch,
}
