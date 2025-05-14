import importlib

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

"""
Command to initialize permissions for all apps in the project.
This command will look for a `permissions_config.py` file in each app's directory
and read the `GROUP_MODEL_PERMISSIONS` dictionary to set up permissions for each model.
The `GROUP_MODEL_PERMISSIONS` dictionary should be structured as follows:
{
    "model_name": {
        "role_enum": ["action1", "action2", ...],
        ...
    }
}
Where `model_name` is the name of the model, `role_enum` is an enumeration value representing a user role,
and `action` is the action to be performed (e.g., "add", "change", "delete", "view").
The command will create groups based on the role enums and assign the corresponding permissions to each group.
"""


class Command(BaseCommand):
    help = "Initialize permissions for all apps"

    def handle(self, *args, **options):
        for app_config in apps.get_app_configs():
            try:
                permissions_module = importlib.import_module(
                    f"{app_config.name}.permissions_config"
                )
            except ModuleNotFoundError:
                continue

            if not hasattr(permissions_module, "GROUP_MODEL_PERMISSIONS"):
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f" App: {app_config.label} "))

            model_perms = permissions_module.GROUP_MODEL_PERMISSIONS

            for model_name, group_map in model_perms.items():
                try:
                    model = apps.get_model(app_config.label, model_name)
                except LookupError:
                    self.stdout.write(
                        self.style.WARNING(
                            f" Model {model_name} not found in {app_config.label} app."
                        )
                    )
                    continue

                ct = ContentType.objects.get_for_model(model)

                for role_enum, actions in group_map.items():
                    group_name = str(role_enum.value).capitalize()
                    group, _ = Group.objects.get_or_create(name=group_name)

                    for action in actions:
                        codename = f"{action}_{model._meta.model_name}"
                        try:
                            perm = Permission.objects.get(
                                content_type=ct, codename=codename
                            )
                            group.permissions.add(perm)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f" Added permission: {codename} ({app_config.label}.{model_name}) to group: {group_name}"
                                )
                            )
                        except Permission.DoesNotExist:
                            self.stdout.write(
                                self.style.WARNING(
                                    f" Permission {codename} does not exist for model {model_name} in {app_config.label} app."
                                )
                            )

        self.stdout.write(
            self.style.MIGRATE_HEADING(" All permissions initialized successfully! ")
        )
