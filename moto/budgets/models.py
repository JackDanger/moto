from collections import defaultdict
from collections.abc import Iterable
from copy import deepcopy
from datetime import datetime
from typing import Any, Optional

from moto.core.base_backend import BackendDict, BaseBackend
from moto.core.common_models import BaseModel
from moto.core.utils import unix_time
from moto.moto_api._internal import mock_random
from moto.utilities.tagging_service import TaggingService
from moto.utilities.utils import PARTITION_NAMES

from .exceptions import (
    BudgetMissingLimit,
    DuplicateRecordException,
    NotFoundException,
)


class Notification(BaseModel):
    def __init__(self, details: dict[str, Any], subscribers: list[dict[str, Any]]):
        self.details = details
        self.subscribers = list(subscribers) if subscribers else []

    def add_subscriber(self, subscriber: dict[str, Any]) -> None:
        self.subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: dict[str, Any]) -> None:
        self.subscribers = [s for s in self.subscribers if s != subscriber]

    def update_subscriber(
        self, old_subscriber: dict[str, Any], new_subscriber: dict[str, Any]
    ) -> None:
        self.subscribers = [
            new_subscriber if s == old_subscriber else s for s in self.subscribers
        ]


class BudgetAction(BaseModel):
    def __init__(
        self,
        account_id: str,
        budget_name: str,
        notification_type: str,
        action_type: str,
        action_threshold: dict[str, Any],
        definition: dict[str, Any],
        execution_role_arn: str,
        approval_model: str,
        subscribers: list[dict[str, Any]],
        region: str,
    ):
        self.action_id = mock_random.get_random_hex(16)
        self.account_id = account_id
        self.budget_name = budget_name
        self.notification_type = notification_type
        self.action_type = action_type
        self.action_threshold = action_threshold
        self.definition = definition
        self.execution_role_arn = execution_role_arn
        self.approval_model = approval_model
        self.subscribers = subscribers or []
        self.status = "STANDBY"
        self.region = region

    def to_dict(self) -> dict[str, Any]:
        return {
            "ActionId": self.action_id,
            "BudgetName": self.budget_name,
            "NotificationType": self.notification_type,
            "ActionType": self.action_type,
            "ActionThreshold": self.action_threshold,
            "Definition": self.definition,
            "ExecutionRoleArn": self.execution_role_arn,
            "ApprovalModel": self.approval_model,
            "Subscribers": self.subscribers,
            "Status": self.status,
        }


class Budget(BaseModel):
    def __init__(self, budget: dict[str, Any], notifications: list[dict[str, Any]]):
        if "BudgetLimit" not in budget and "PlannedBudgetLimits" not in budget:
            raise BudgetMissingLimit()
        # Storing the budget as a Dict for now - if we need more control, we can always read/write it back
        self.budget = budget
        self.notifications = [
            Notification(details=x["Notification"], subscribers=x["Subscribers"])
            for x in notifications
        ]
        self.budget["LastUpdatedTime"] = unix_time()
        if "TimePeriod" not in self.budget:
            first_day_of_month = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            self.budget["TimePeriod"] = {
                "Start": unix_time(first_day_of_month),
                "End": 3706473600,  # "2087-06-15T00:00:00+00:00"
            }

    def to_dict(self) -> dict[str, Any]:
        cp = deepcopy(self.budget)
        if "CalculatedSpend" not in cp:
            cp["CalculatedSpend"] = {
                "ActualSpend": {"Amount": "0", "Unit": "USD"},
                "ForecastedSpend": {"Amount": "0", "Unit": "USD"},
            }
        if self.budget["BudgetType"] == "COST" and "CostTypes" not in cp:
            cp["CostTypes"] = {
                "IncludeCredit": True,
                "IncludeDiscount": True,
                "IncludeOtherSubscription": True,
                "IncludeRecurring": True,
                "IncludeRefund": True,
                "IncludeSubscription": True,
                "IncludeSupport": True,
                "IncludeTax": True,
                "IncludeUpfront": True,
                "UseAmortized": False,
                "UseBlended": False,
            }
        return cp

    def add_notification(
        self, details: dict[str, Any], subscribers: list[dict[str, Any]]
    ) -> None:
        self.notifications.append(Notification(details, subscribers))

    def delete_notification(self, details: dict[str, Any]) -> None:
        self.notifications = [n for n in self.notifications if n.details != details]

    def get_notifications(self) -> Iterable[dict[str, Any]]:
        return [n.details for n in self.notifications]

    def find_notification(self, notification: dict[str, Any]) -> Optional[Notification]:
        for n in self.notifications:
            if n.details == notification:
                return n
        return None

    def update_notification(
        self, old_notification: dict[str, Any], new_notification: dict[str, Any]
    ) -> None:
        for n in self.notifications:
            if n.details == old_notification:
                n.details = new_notification
                return


class BudgetsBackend(BaseBackend):
    """Implementation of Budgets APIs."""

    def __init__(self, region_name: str, account_id: str):
        super().__init__(region_name, account_id)
        self.budgets: dict[str, dict[str, Budget]] = defaultdict(dict)
        self.actions: dict[str, dict[str, BudgetAction]] = defaultdict(dict)
        self.tagger = TaggingService()

    def _get_budget(self, account_id: str, budget_name: str) -> Budget:
        if budget_name not in self.budgets[account_id]:
            raise NotFoundException(
                f"Unable to get budget: {budget_name} - the budget doesn't exist."
            )
        return self.budgets[account_id][budget_name]

    def _get_action(self, account_id: str, action_id: str) -> BudgetAction:
        if action_id not in self.actions[account_id]:
            raise NotFoundException(
                f"Unable to get action: {action_id} - the action doesn't exist."
            )
        return self.actions[account_id][action_id]

    def _budget_arn(self, account_id: str, budget_name: str) -> str:
        return f"arn:aws:budgets::{account_id}:budget/{budget_name}"

    # --- Budgets ---

    def create_budget(
        self,
        account_id: str,
        budget: dict[str, Any],
        notifications: list[dict[str, Any]],
    ) -> None:
        budget_name = budget["BudgetName"]
        if budget_name in self.budgets[account_id]:
            raise DuplicateRecordException(
                record_type="budget", record_name=budget_name
            )
        self.budgets[account_id][budget_name] = Budget(budget, notifications)

    def describe_budget(self, account_id: str, budget_name: str) -> dict[str, Any]:
        return self._get_budget(account_id, budget_name).to_dict()

    def describe_budgets(self, account_id: str) -> Iterable[dict[str, Any]]:
        """
        Pagination is not yet implemented
        """
        return [budget.to_dict() for budget in self.budgets[account_id].values()]

    def update_budget(self, account_id: str, new_budget: dict[str, Any]) -> None:
        budget_name = new_budget.get("BudgetName", "")
        if budget_name not in self.budgets[account_id]:
            raise NotFoundException(
                f"Unable to update budget: {budget_name} - the budget doesn't exist."
            )
        existing = self.budgets[account_id][budget_name]
        existing.budget.update(new_budget)
        existing.budget["LastUpdatedTime"] = unix_time()

    def delete_budget(self, account_id: str, budget_name: str) -> None:
        if budget_name not in self.budgets[account_id]:
            msg = f"Unable to delete budget: {budget_name} - the budget doesn't exist. Try creating it first. "
            raise NotFoundException(msg)
        self.budgets[account_id].pop(budget_name)

    # --- Notifications ---

    def create_notification(
        self,
        account_id: str,
        budget_name: str,
        notification: dict[str, Any],
        subscribers: list[dict[str, Any]],
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        budget.add_notification(details=notification, subscribers=subscribers)

    def delete_notification(
        self, account_id: str, budget_name: str, notification: dict[str, Any]
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        budget.delete_notification(details=notification)

    def update_notification(
        self,
        account_id: str,
        budget_name: str,
        old_notification: dict[str, Any],
        new_notification: dict[str, Any],
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        budget.update_notification(old_notification, new_notification)

    def describe_notifications_for_budget(
        self, account_id: str, budget_name: str
    ) -> Iterable[dict[str, Any]]:
        """
        Pagination has not yet been implemented
        """
        return self._get_budget(account_id, budget_name).get_notifications()

    def describe_budget_notifications_for_account(
        self, account_id: str
    ) -> list[dict[str, Any]]:
        result = []
        for budget_name, budget in self.budgets[account_id].items():
            notifications = list(budget.get_notifications())
            if notifications:
                result.append(
                    {
                        "BudgetName": budget_name,
                        "Notifications": notifications,
                    }
                )
        return result

    # --- Subscribers ---

    def create_subscriber(
        self,
        account_id: str,
        budget_name: str,
        notification: dict[str, Any],
        subscriber: dict[str, Any],
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        notif = budget.find_notification(notification)
        if notif is None:
            raise NotFoundException(
                "Unable to create subscriber - the notification doesn't exist."
            )
        notif.add_subscriber(subscriber)

    def delete_subscriber(
        self,
        account_id: str,
        budget_name: str,
        notification: dict[str, Any],
        subscriber: dict[str, Any],
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        notif = budget.find_notification(notification)
        if notif is None:
            raise NotFoundException(
                "Unable to delete subscriber - the notification doesn't exist."
            )
        notif.remove_subscriber(subscriber)

    def update_subscriber(
        self,
        account_id: str,
        budget_name: str,
        notification: dict[str, Any],
        old_subscriber: dict[str, Any],
        new_subscriber: dict[str, Any],
    ) -> None:
        budget = self._get_budget(account_id, budget_name)
        notif = budget.find_notification(notification)
        if notif is None:
            raise NotFoundException(
                "Unable to update subscriber - the notification doesn't exist."
            )
        notif.update_subscriber(old_subscriber, new_subscriber)

    def describe_subscribers_for_notification(
        self,
        account_id: str,
        budget_name: str,
        notification: dict[str, Any],
    ) -> list[dict[str, Any]]:
        budget = self._get_budget(account_id, budget_name)
        notif = budget.find_notification(notification)
        if notif is None:
            raise NotFoundException(
                "Unable to get subscribers - the notification doesn't exist."
            )
        return notif.subscribers

    # --- Budget Actions ---

    def create_budget_action(
        self,
        account_id: str,
        budget_name: str,
        notification_type: str,
        action_type: str,
        action_threshold: dict[str, Any],
        definition: dict[str, Any],
        execution_role_arn: str,
        approval_model: str,
        subscribers: list[dict[str, Any]],
    ) -> BudgetAction:
        # Verify budget exists
        self._get_budget(account_id, budget_name)
        action = BudgetAction(
            account_id=account_id,
            budget_name=budget_name,
            notification_type=notification_type,
            action_type=action_type,
            action_threshold=action_threshold,
            definition=definition,
            execution_role_arn=execution_role_arn,
            approval_model=approval_model,
            subscribers=subscribers,
            region=self.region_name,
        )
        self.actions[account_id][action.action_id] = action
        return action

    def describe_budget_action(
        self, account_id: str, budget_name: str, action_id: str
    ) -> BudgetAction:
        self._get_budget(account_id, budget_name)
        return self._get_action(account_id, action_id)

    def delete_budget_action(
        self, account_id: str, budget_name: str, action_id: str
    ) -> BudgetAction:
        self._get_budget(account_id, budget_name)
        action = self._get_action(account_id, action_id)
        self.actions[account_id].pop(action_id)
        return action

    def update_budget_action(
        self,
        account_id: str,
        budget_name: str,
        action_id: str,
        notification_type: Optional[str],
        action_threshold: Optional[dict[str, Any]],
        definition: Optional[dict[str, Any]],
        execution_role_arn: Optional[str],
        approval_model: Optional[str],
        subscribers: Optional[list[dict[str, Any]]],
    ) -> tuple[BudgetAction, BudgetAction]:
        self._get_budget(account_id, budget_name)
        action = self._get_action(account_id, action_id)
        old_action = BudgetAction(
            account_id=action.account_id,
            budget_name=action.budget_name,
            notification_type=action.notification_type,
            action_type=action.action_type,
            action_threshold=deepcopy(action.action_threshold),
            definition=deepcopy(action.definition),
            execution_role_arn=action.execution_role_arn,
            approval_model=action.approval_model,
            subscribers=deepcopy(action.subscribers),
            region=action.region,
        )
        old_action.action_id = action.action_id
        old_action.status = action.status
        if notification_type is not None:
            action.notification_type = notification_type
        if action_threshold is not None:
            action.action_threshold = action_threshold
        if definition is not None:
            action.definition = definition
        if execution_role_arn is not None:
            action.execution_role_arn = execution_role_arn
        if approval_model is not None:
            action.approval_model = approval_model
        if subscribers is not None:
            action.subscribers = subscribers
        return old_action, action

    def execute_budget_action(
        self, account_id: str, budget_name: str, action_id: str, execution_type: str
    ) -> dict[str, str]:
        self._get_budget(account_id, budget_name)
        action = self._get_action(account_id, action_id)
        if execution_type == "APPROVE_BUDGET_ACTION":
            action.status = "EXECUTION_SUCCESS"
        elif execution_type == "RETRY_BUDGET_ACTION":
            action.status = "EXECUTION_SUCCESS"
        elif execution_type == "REVERSE_BUDGET_ACTION":
            action.status = "REVERSE_SUCCESS"
        elif execution_type == "RESET_BUDGET_ACTION":
            action.status = "STANDBY"
        return {
            "AccountId": account_id,
            "BudgetName": budget_name,
            "ActionId": action_id,
            "ExecutionType": execution_type,
        }

    def describe_budget_actions_for_account(
        self, account_id: str
    ) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self.actions[account_id].values()]

    def describe_budget_actions_for_budget(
        self, account_id: str, budget_name: str
    ) -> list[dict[str, Any]]:
        self._get_budget(account_id, budget_name)
        return [
            a.to_dict()
            for a in self.actions[account_id].values()
            if a.budget_name == budget_name
        ]

    def describe_budget_action_histories(
        self, account_id: str, budget_name: str, action_id: str
    ) -> list[dict[str, Any]]:
        self._get_budget(account_id, budget_name)
        self._get_action(account_id, action_id)
        # Return empty history - we don't track action execution history
        return []

    def describe_budget_performance_history(
        self, account_id: str, budget_name: str
    ) -> dict[str, Any]:
        budget = self._get_budget(account_id, budget_name)
        return {
            "BudgetName": budget_name,
            "BudgetType": budget.budget.get("BudgetType", "COST"),
            "CostTypes": budget.to_dict().get("CostTypes", {}),
            "TimeUnit": budget.budget.get("TimeUnit", "MONTHLY"),
            "BudgetedAndActualAmountsList": [],
        }

    # --- Tags ---

    def list_tags_for_resource(self, resource_arn: str) -> list[dict[str, str]]:
        tags = self.tagger.get_tag_dict_for_resource(resource_arn)
        return [{"Key": k, "Value": v} for k, v in tags.items()]

    def tag_resource(
        self, resource_arn: str, resource_tags: list[dict[str, str]]
    ) -> None:
        tag_list = [
            {"Key": t["Key"], "Value": t.get("Value", "")} for t in resource_tags
        ]
        self.tagger.tag_resource(resource_arn, tag_list)

    def untag_resource(
        self, resource_arn: str, resource_tag_keys: list[str]
    ) -> None:
        self.tagger.untag_resource_using_names(resource_arn, resource_tag_keys)


budgets_backends = BackendDict(
    BudgetsBackend,
    "budgets",
    use_boto3_regions=False,
    additional_regions=PARTITION_NAMES,
)
