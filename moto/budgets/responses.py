import json

from moto.core.responses import BaseResponse

from .models import BudgetsBackend, budgets_backends


class BudgetsResponse(BaseResponse):
    def __init__(self) -> None:
        super().__init__(service_name="budgets")

    @property
    def backend(self) -> BudgetsBackend:
        return budgets_backends[self.current_account][self.partition]

    # --- Budgets ---

    def create_budget(self) -> str:
        account_id = self._get_param("AccountId")
        budget = self._get_param("Budget")
        notifications = self._get_param("NotificationsWithSubscribers", [])
        self.backend.create_budget(
            account_id=account_id, budget=budget, notifications=notifications
        )
        return json.dumps({})

    def describe_budget(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        budget = self.backend.describe_budget(
            account_id=account_id, budget_name=budget_name
        )
        return json.dumps({"Budget": budget})

    def describe_budgets(self) -> str:
        account_id = self._get_param("AccountId")
        budgets = self.backend.describe_budgets(account_id=account_id)
        return json.dumps({"Budgets": budgets, "nextToken": None})

    def update_budget(self) -> str:
        account_id = self._get_param("AccountId")
        new_budget = self._get_param("NewBudget")
        self.backend.update_budget(account_id=account_id, new_budget=new_budget)
        return json.dumps({})

    def delete_budget(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        self.backend.delete_budget(account_id=account_id, budget_name=budget_name)
        return json.dumps({})

    # --- Notifications ---

    def create_notification(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        subscribers = self._get_param("Subscribers")
        self.backend.create_notification(
            account_id=account_id,
            budget_name=budget_name,
            notification=notification,
            subscribers=subscribers,
        )
        return json.dumps({})

    def delete_notification(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        self.backend.delete_notification(
            account_id=account_id, budget_name=budget_name, notification=notification
        )
        return json.dumps({})

    def update_notification(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        old_notification = self._get_param("OldNotification")
        new_notification = self._get_param("NewNotification")
        self.backend.update_notification(
            account_id=account_id,
            budget_name=budget_name,
            old_notification=old_notification,
            new_notification=new_notification,
        )
        return json.dumps({})

    def describe_notifications_for_budget(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notifications = self.backend.describe_notifications_for_budget(
            account_id=account_id, budget_name=budget_name
        )
        return json.dumps({"Notifications": notifications, "NextToken": None})

    def describe_budget_notifications_for_account(self) -> str:
        account_id = self._get_param("AccountId")
        result = self.backend.describe_budget_notifications_for_account(
            account_id=account_id
        )
        return json.dumps(
            {"BudgetNotificationsForAccount": result, "NextToken": None}
        )

    # --- Subscribers ---

    def create_subscriber(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        subscriber = self._get_param("Subscriber")
        self.backend.create_subscriber(
            account_id=account_id,
            budget_name=budget_name,
            notification=notification,
            subscriber=subscriber,
        )
        return json.dumps({})

    def delete_subscriber(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        subscriber = self._get_param("Subscriber")
        self.backend.delete_subscriber(
            account_id=account_id,
            budget_name=budget_name,
            notification=notification,
            subscriber=subscriber,
        )
        return json.dumps({})

    def update_subscriber(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        old_subscriber = self._get_param("OldSubscriber")
        new_subscriber = self._get_param("NewSubscriber")
        self.backend.update_subscriber(
            account_id=account_id,
            budget_name=budget_name,
            notification=notification,
            old_subscriber=old_subscriber,
            new_subscriber=new_subscriber,
        )
        return json.dumps({})

    def describe_subscribers_for_notification(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification = self._get_param("Notification")
        subscribers = self.backend.describe_subscribers_for_notification(
            account_id=account_id,
            budget_name=budget_name,
            notification=notification,
        )
        return json.dumps({"Subscribers": subscribers, "NextToken": None})

    # --- Budget Actions ---

    def create_budget_action(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        notification_type = self._get_param("NotificationType")
        action_type = self._get_param("ActionType")
        action_threshold = self._get_param("ActionThreshold")
        definition = self._get_param("Definition")
        execution_role_arn = self._get_param("ExecutionRoleArn")
        approval_model = self._get_param("ApprovalModel")
        subscribers = self._get_param("Subscribers")
        action = self.backend.create_budget_action(
            account_id=account_id,
            budget_name=budget_name,
            notification_type=notification_type,
            action_type=action_type,
            action_threshold=action_threshold,
            definition=definition,
            execution_role_arn=execution_role_arn,
            approval_model=approval_model,
            subscribers=subscribers,
        )
        return json.dumps(
            {
                "AccountId": account_id,
                "BudgetName": budget_name,
                "ActionId": action.action_id,
            }
        )

    def describe_budget_action(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        action_id = self._get_param("ActionId")
        action = self.backend.describe_budget_action(
            account_id=account_id, budget_name=budget_name, action_id=action_id
        )
        return json.dumps(
            {
                "AccountId": account_id,
                "BudgetName": budget_name,
                "Action": action.to_dict(),
            }
        )

    def delete_budget_action(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        action_id = self._get_param("ActionId")
        action = self.backend.delete_budget_action(
            account_id=account_id, budget_name=budget_name, action_id=action_id
        )
        return json.dumps(
            {
                "AccountId": account_id,
                "BudgetName": budget_name,
                "Action": action.to_dict(),
            }
        )

    def update_budget_action(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        action_id = self._get_param("ActionId")
        notification_type = self._get_param("NotificationType")
        action_threshold = self._get_param("ActionThreshold")
        definition = self._get_param("Definition")
        execution_role_arn = self._get_param("ExecutionRoleArn")
        approval_model = self._get_param("ApprovalModel")
        subscribers = self._get_param("Subscribers")
        old_action, new_action = self.backend.update_budget_action(
            account_id=account_id,
            budget_name=budget_name,
            action_id=action_id,
            notification_type=notification_type,
            action_threshold=action_threshold,
            definition=definition,
            execution_role_arn=execution_role_arn,
            approval_model=approval_model,
            subscribers=subscribers,
        )
        return json.dumps(
            {
                "AccountId": account_id,
                "BudgetName": budget_name,
                "OldAction": old_action.to_dict(),
                "NewAction": new_action.to_dict(),
            }
        )

    def execute_budget_action(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        action_id = self._get_param("ActionId")
        execution_type = self._get_param("ExecutionType")
        result = self.backend.execute_budget_action(
            account_id=account_id,
            budget_name=budget_name,
            action_id=action_id,
            execution_type=execution_type,
        )
        return json.dumps(result)

    def describe_budget_actions_for_account(self) -> str:
        account_id = self._get_param("AccountId")
        actions = self.backend.describe_budget_actions_for_account(
            account_id=account_id
        )
        return json.dumps({"Actions": actions, "NextToken": None})

    def describe_budget_actions_for_budget(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        actions = self.backend.describe_budget_actions_for_budget(
            account_id=account_id, budget_name=budget_name
        )
        return json.dumps({"Actions": actions, "NextToken": None})

    def describe_budget_action_histories(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        action_id = self._get_param("ActionId")
        histories = self.backend.describe_budget_action_histories(
            account_id=account_id, budget_name=budget_name, action_id=action_id
        )
        return json.dumps({"ActionHistories": histories, "NextToken": None})

    def describe_budget_performance_history(self) -> str:
        account_id = self._get_param("AccountId")
        budget_name = self._get_param("BudgetName")
        history = self.backend.describe_budget_performance_history(
            account_id=account_id, budget_name=budget_name
        )
        return json.dumps({"BudgetPerformanceHistory": history, "NextToken": None})

    # --- Tags ---

    def list_tags_for_resource(self) -> str:
        resource_arn = self._get_param("ResourceARN")
        tags = self.backend.list_tags_for_resource(resource_arn=resource_arn)
        return json.dumps({"ResourceTags": tags})

    def tag_resource(self) -> str:
        resource_arn = self._get_param("ResourceARN")
        resource_tags = self._get_param("ResourceTags")
        self.backend.tag_resource(
            resource_arn=resource_arn, resource_tags=resource_tags
        )
        return json.dumps({})

    def untag_resource(self) -> str:
        resource_arn = self._get_param("ResourceARN")
        resource_tag_keys = self._get_param("ResourceTagKeys")
        self.backend.untag_resource(
            resource_arn=resource_arn, resource_tag_keys=resource_tag_keys
        )
        return json.dumps({})
