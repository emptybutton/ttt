from dataclasses import dataclass


@dataclass(frozen=True)
class AdminRightViaAdminToken:
    ...


@dataclass(frozen=True)
class AdminRightViaOtherAdmin:
    admin_id: int


type AdminRight = AdminRightViaAdminToken | AdminRightViaOtherAdmin
