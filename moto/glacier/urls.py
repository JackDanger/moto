from .responses import GlacierResponse

url_bases = [r"https?://glacier\.(.+)\.amazonaws.com"]

url_paths = {
    # Data retrieval policy
    "{0}/(?P<account_number>.+)/policies/data-retrieval$": GlacierResponse.dispatch,
    # Provisioned capacity
    "{0}/(?P<account_number>.+)/provisioned-capacity$": GlacierResponse.dispatch,
    # Vault list
    "{0}/(?P<account_number>.+)/vaults$": GlacierResponse.dispatch,
    # Vault tags
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/tags$": GlacierResponse.dispatch,
    # Vault notification configuration
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/notification-configuration$": GlacierResponse.dispatch,
    # Vault access policy
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/access-policy$": GlacierResponse.dispatch,
    # Vault lock policy with lock ID (must come before lock-policy without ID)
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/lock-policy/(?P<lock_id>[^/]+)$": GlacierResponse.dispatch,
    # Vault lock policy
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/lock-policy$": GlacierResponse.dispatch,
    # Multipart upload parts / specific upload
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/multipart-uploads/(?P<upload_id>[^/]+)$": GlacierResponse.dispatch,
    # Multipart uploads list / initiate
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/multipart-uploads$": GlacierResponse.dispatch,
    # Vault (describe/create/delete) - use [^/]+ to avoid matching sub-paths
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)$": GlacierResponse.dispatch,
    # Archives
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/archives$": GlacierResponse.dispatch,
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/archives/(?P<archive_id>.+)$": GlacierResponse.dispatch,
    # Jobs
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/jobs$": GlacierResponse.dispatch,
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/jobs/(?P<job_id>[^/.]+)$": GlacierResponse.dispatch,
    "{0}/(?P<account_number>.+)/vaults/(?P<vault_name>[^/]+)/jobs/(?P<job_id>.+)/output$": GlacierResponse.dispatch,
}
