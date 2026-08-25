from typing import Any, Optional

from moto.core.utils import iso_8601_datetime_with_milliseconds, utcnow

from ..utils import (
    random_capacity_reservation_fleet_id,
    random_capacity_reservation_id,
)
from .core import TaggedEC2Resource


class CapacityReservation(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        instance_type: str,
        instance_platform: str,
        availability_zone: str,
        instance_count: int = 1,
        tenancy: str = "default",
        ebs_optimized: bool = False,
        ephemeral_storage: bool = False,
        end_date: Optional[str] = None,
        end_date_type: str = "unlimited",
        instance_match_criteria: str = "open",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_capacity_reservation_id()
        self.instance_type = instance_type
        self.instance_platform = instance_platform
        self.availability_zone = availability_zone
        self.instance_count = instance_count
        self.tenancy = tenancy
        self.ebs_optimized = ebs_optimized
        self.ephemeral_storage = ephemeral_storage
        self.end_date = end_date
        self.end_date_type = end_date_type
        self.instance_match_criteria = instance_match_criteria
        self.state = "active"
        self.available_instance_count = instance_count
        self.total_instance_count = instance_count
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_date(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)

    @property
    def owner_id(self) -> str:
        return self.ec2_backend.account_id

    @property
    def arn(self) -> str:
        return (
            f"arn:{self.ec2_backend.partition}:ec2:{self.ec2_backend.region_name}"
            f":{self.ec2_backend.account_id}:capacity-reservation/{self.id}"
        )


class CapacityReservationFleet(TaggedEC2Resource):
    def __init__(
        self,
        ec2_backend: Any,
        instance_type_specifications: list[dict[str, Any]],
        total_target_capacity: int,
        allocation_strategy: str = "prioritized",
        tenancy: str = "default",
        end_date: Optional[str] = None,
        instance_match_criteria: str = "open",
        tags: Optional[dict[str, str]] = None,
    ):
        self.ec2_backend = ec2_backend
        self.id = random_capacity_reservation_fleet_id()
        self.instance_type_specifications = instance_type_specifications
        self.total_target_capacity = total_target_capacity
        self.allocation_strategy = allocation_strategy
        self.tenancy = tenancy
        self.end_date = end_date
        self.instance_match_criteria = instance_match_criteria
        self.state = "active"
        self.total_fulfilled_capacity = float(total_target_capacity)
        self._created_at = utcnow()
        self.add_tags(tags or {})

    @property
    def creation_time(self) -> str:
        return iso_8601_datetime_with_milliseconds(self._created_at)


class CapacityReservationBackend:
    def __init__(self) -> None:
        self.capacity_reservations: dict[str, CapacityReservation] = {}
        self.capacity_reservation_fleets: dict[str, CapacityReservationFleet] = {}

    def create_capacity_reservation(
        self,
        instance_type: str,
        instance_platform: str,
        availability_zone: str,
        instance_count: int = 1,
        tenancy: str = "default",
        ebs_optimized: bool = False,
        ephemeral_storage: bool = False,
        end_date: Optional[str] = None,
        end_date_type: str = "unlimited",
        instance_match_criteria: str = "open",
        tags: Optional[dict[str, str]] = None,
    ) -> CapacityReservation:
        cr = CapacityReservation(
            self,
            instance_type=instance_type,
            instance_platform=instance_platform,
            availability_zone=availability_zone,
            instance_count=instance_count,
            tenancy=tenancy,
            ebs_optimized=ebs_optimized,
            ephemeral_storage=ephemeral_storage,
            end_date=end_date,
            end_date_type=end_date_type,
            instance_match_criteria=instance_match_criteria,
            tags=tags,
        )
        self.capacity_reservations[cr.id] = cr
        return cr

    def describe_capacity_reservations(
        self,
        capacity_reservation_ids: Optional[list[str]] = None,
    ) -> list[CapacityReservation]:
        crs = list(self.capacity_reservations.values())
        if capacity_reservation_ids:
            crs = [c for c in crs if c.id in capacity_reservation_ids]
        return crs

    def modify_capacity_reservation(
        self,
        capacity_reservation_id: str,
        instance_count: Optional[int] = None,
        end_date: Optional[str] = None,
        end_date_type: Optional[str] = None,
    ) -> CapacityReservation:
        cr = self.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            from ..exceptions import InvalidCapacityReservationIdError

            raise InvalidCapacityReservationIdError(capacity_reservation_id)
        if instance_count is not None:
            cr.instance_count = instance_count
            cr.total_instance_count = instance_count
            cr.available_instance_count = instance_count
        if end_date is not None:
            cr.end_date = end_date
        if end_date_type is not None:
            cr.end_date_type = end_date_type
        return cr

    def cancel_capacity_reservation(
        self,
        capacity_reservation_id: str,
    ) -> CapacityReservation:
        cr = self.capacity_reservations.get(capacity_reservation_id)
        if not cr:
            from ..exceptions import InvalidCapacityReservationIdError

            raise InvalidCapacityReservationIdError(capacity_reservation_id)
        cr.state = "cancelled"
        return cr

    def create_capacity_reservation_fleet(
        self,
        instance_type_specifications: list[dict[str, Any]],
        total_target_capacity: int,
        allocation_strategy: str = "prioritized",
        tenancy: str = "default",
        end_date: Optional[str] = None,
        instance_match_criteria: str = "open",
        tags: Optional[dict[str, str]] = None,
    ) -> CapacityReservationFleet:
        fleet = CapacityReservationFleet(
            self,
            instance_type_specifications=instance_type_specifications,
            total_target_capacity=total_target_capacity,
            allocation_strategy=allocation_strategy,
            tenancy=tenancy,
            end_date=end_date,
            instance_match_criteria=instance_match_criteria,
            tags=tags,
        )
        self.capacity_reservation_fleets[fleet.id] = fleet
        return fleet

    def describe_capacity_reservation_fleets(
        self,
        capacity_reservation_fleet_ids: Optional[list[str]] = None,
    ) -> list[CapacityReservationFleet]:
        fleets = list(self.capacity_reservation_fleets.values())
        if capacity_reservation_fleet_ids:
            fleets = [
                f for f in fleets if f.id in capacity_reservation_fleet_ids
            ]
        return fleets

    def modify_capacity_reservation_fleet(
        self,
        capacity_reservation_fleet_id: str,
        total_target_capacity: Optional[int] = None,
        end_date: Optional[str] = None,
    ) -> CapacityReservationFleet:
        fleet = self.capacity_reservation_fleets.get(
            capacity_reservation_fleet_id
        )
        if not fleet:
            from ..exceptions import InvalidCapacityReservationFleetIdError

            raise InvalidCapacityReservationFleetIdError(
                capacity_reservation_fleet_id
            )
        if total_target_capacity is not None:
            fleet.total_target_capacity = total_target_capacity
            fleet.total_fulfilled_capacity = float(total_target_capacity)
        if end_date is not None:
            fleet.end_date = end_date
        return fleet

    def cancel_capacity_reservation_fleets(
        self,
        capacity_reservation_fleet_ids: list[str],
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for fleet_id in capacity_reservation_fleet_ids:
            fleet = self.capacity_reservation_fleets.get(fleet_id)
            if fleet:
                fleet.state = "cancelled"
                results.append(
                    {
                        "capacity_reservation_fleet_id": fleet_id,
                        "current_state": "cancelled",
                        "previous_state": "active",
                    }
                )
            else:
                results.append(
                    {
                        "capacity_reservation_fleet_id": fleet_id,
                        "error": "InvalidCapacityReservationFleetId.NotFound",
                    }
                )
        return results
