from apps.core.enums import Role

"""Permissions configuration for the application."""

GROUP_MODEL_PERMISSIONS = {
    "company": {
        Role.ADMIN: ["add", "change", "delete", "view"],
        Role.OWNER: ["add", "change", "view"],
        Role.MANAGER: ["view", "change"],
        Role.WORKER: ["view"],
        Role.VIEWER: ["view"],
    },
    "address": {
        Role.ADMIN: ["add", "change", "delete", "view"],
        Role.OWNER: ["add", "change", "view"],
        Role.MANAGER: ["add", "change", "view"],
        Role.WORKER: ["view"],
        Role.VIEWER: ["view"],
    },
    "customuser": {
        Role.ADMIN: ["add", "change", "delete", "view"],
        Role.OWNER: ["add", "change", "view"],
        Role.MANAGER: ["add", "change", "view"],
        Role.WORKER: ["view"],
        Role.VIEWER: ["view"],
    },
}
