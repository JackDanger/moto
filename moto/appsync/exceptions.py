import json

from moto.core.exceptions import JsonRESTError


class AppSyncExceptions(JsonRESTError):
    pass


class AWSValidationException(AppSyncExceptions):
    code = 400

    def __init__(self, message: str):
        super().__init__("ValidationException", message)
        self.description = json.dumps({"message": self.message})


class ApiKeyValidityOutOfBoundsException(AppSyncExceptions):
    code = 400

    def __init__(self, message: str):
        super().__init__("ApiKeyValidityOutOfBoundsException", message)
        self.description = json.dumps({"message": self.message})


class GraphqlAPINotFound(AppSyncExceptions):
    code = 404

    def __init__(self, api_id: str):
        super().__init__("NotFoundException", f"GraphQL API {api_id} not found.")
        self.description = json.dumps({"message": self.message})


class GraphQLSchemaException(AppSyncExceptions):
    code = 400

    def __init__(self, message: str):
        super().__init__("GraphQLSchemaException", message)
        self.description = json.dumps({"message": self.message})


class GraphqlAPICacheNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, op: str):
        super().__init__(
            "NotFoundException",
            f"Unable to {op} the cache as it doesn't exist, please create the cache first.",
        )
        self.description = json.dumps({"message": self.message})


class EventsAPINotFound(AppSyncExceptions):
    code = 404

    def __init__(self, api_id: str):
        super().__init__("NotFoundException", f"Events API {api_id} not found.")
        self.description = json.dumps({"message": self.message})


class BadRequestException(AppSyncExceptions):
    def __init__(self, message: str):
        super().__init__("BadRequestException", message)


class DataSourceNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, name: str):
        super().__init__("NotFoundException", f"DataSource {name} not found.")
        self.description = json.dumps({"message": self.message})


class TypeNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, name: str):
        super().__init__("NotFoundException", f"Type {name} not found.")
        self.description = json.dumps({"message": self.message})


class ResolverNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, type_name: str, field_name: str):
        super().__init__(
            "NotFoundException",
            f"Resolver {type_name}/{field_name} not found.",
        )
        self.description = json.dumps({"message": self.message})


class FunctionNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, function_id: str):
        super().__init__(
            "NotFoundException",
            f"Function {function_id} not found.",
        )
        self.description = json.dumps({"message": self.message})


class DomainNameNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, domain_name: str):
        super().__init__(
            "NotFoundException",
            f"Domain name {domain_name} not found.",
        )
        self.description = json.dumps({"message": self.message})


class ApiAssociationNotFound(AppSyncExceptions):
    code = 404

    def __init__(self, domain_name: str):
        super().__init__(
            "NotFoundException",
            f"No API association found for domain {domain_name}.",
        )
        self.description = json.dumps({"message": self.message})
