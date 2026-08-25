"""Exceptions raised by the pinpoint service."""

from moto.core.exceptions import JsonRESTError


class PinpointExceptions(JsonRESTError):
    pass


class ApplicationNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Application not found")


class EventStreamNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Resource not found")


class CampaignNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Campaign not found")


class SegmentNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Segment not found")


class JourneyNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Journey not found")


class TemplateNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Template not found")


class EndpointNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Endpoint not found")


class ExportJobNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Export job not found")


class ImportJobNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Import job not found")


class RecommenderNotFound(PinpointExceptions):
    code = 404

    def __init__(self) -> None:
        super().__init__("NotFoundException", "Recommender configuration not found")
