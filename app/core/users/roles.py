from typing import Dict, Set
from app.core.users.constants import RolesEnum


class RoleManager:
    def __init__(self):
        self._roles: Dict[RolesEnum, Set[int]] = {role: set() for role in RolesEnum}

    def add_member(self, role: RolesEnum, user_id: int):
        self._roles[role].add(user_id)

    def remove_member(self, role: RolesEnum, user_id: int):
        self._roles[role].discard(user_id)

    def has_member(self, role: RolesEnum, user_id: int) -> bool:
        return user_id in self._roles.get(role, set())

    def get_members(self, role: RolesEnum) -> Set[int]:
        return self._roles.get(role, set())