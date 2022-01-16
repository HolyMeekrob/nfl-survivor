from flask_principal import Permission, RoleNeed
from survivor.data.models.role import Role

is_admin = Permission(RoleNeed(Role.ADMIN))
