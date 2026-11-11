"""A simple, explicit, revocable permission registry.

Every tool declares a `required_permission` string (see
`agentdesk.agent.tools.Tool`); the agent checks that permission against
this registry before invoking the tool, so a user can see and revoke
exactly what the agent is allowed to do.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PermissionInfo:
    """Describes one permission for display purposes.

    Attributes:
        name: The permission's unique key, e.g. `"email.read"`.
        label: A short, human-readable name.
        description: A one-sentence explanation of what it allows.
    """

    name: str
    label: str
    description: str


# The fixed set of permissions this project defines. New tools should
# reuse one of these rather than inventing ad hoc permission strings.
KNOWN_PERMISSIONS: tuple[PermissionInfo, ...] = (
    PermissionInfo(
        name="email.read",
        label="Read mock inbox",
        description="Lets the agent read and search the sample email inbox.",
    ),
    PermissionInfo(
        name="files.read",
        label="List mock files",
        description="Lets the agent list entries in the sample file tree.",
    ),
    PermissionInfo(
        name="workflows.write",
        label="Create workflows",
        description="Lets the agent save new multi-step workflows.",
    ),
    PermissionInfo(
        name="workflows.run",
        label="Run workflows",
        description="Lets the agent execute previously saved workflows.",
    ),
)


@dataclass
class PermissionRegistry:
    """Tracks which permissions are currently granted.

    All known permissions default to granted, so the app is immediately
    usable; a user can revoke any of them (e.g. from a Permissions
    screen) to see the agent refuse the corresponding tool calls.

    Attributes:
        granted: Maps permission name to whether it is currently granted.
    """

    granted: dict[str, bool] = field(
        default_factory=lambda: {info.name: True for info in KNOWN_PERMISSIONS}
    )

    def is_granted(self, permission: str) -> bool:
        """Checks whether a permission is currently granted.

        Args:
            permission: The permission name to check.

        Returns:
            True if granted. Unknown permission names are treated as not
            granted (fail closed).
        """
        return self.granted.get(permission, False)

    def set_granted(self, permission: str, value: bool) -> None:
        """Grants or revokes a permission.

        Args:
            permission: The permission name to change.
            value: True to grant it, False to revoke it.
        """
        self.granted[permission] = value
