from dataclasses import dataclass


@dataclass(frozen=True)
class RootAdminRole: ...


AdminRole = RootAdminRole


@dataclass(frozen=True)
class RegularUserRole: ...


type Role = RegularUserRole | RootAdminRole
