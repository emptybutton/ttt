from dataclasses import dataclass


@dataclass(frozen=True)
class RootAdminRole: ...


@dataclass(frozen=True)
class NotRootAdminRole:
    root_admin_id: int


AdminRole = RootAdminRole | NotRootAdminRole


@dataclass(frozen=True)
class RegularUserRole: ...


type Role = RegularUserRole | AdminRole
