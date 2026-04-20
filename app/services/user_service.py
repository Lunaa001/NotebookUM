class UserRepository:
    def get_by_id(self, user_id: int):
        raise NotImplementedError

    def get_by_email(self, email: str):
        raise NotImplementedError

    def create(self, *, nombre: str, email: str, password_hash: str):
        raise NotImplementedError

    def update(
        self,
        user_id: int,
        *,
        nombre: str | None = None,
        email: str | None = None,
        password_hash: str | None = None,
    ):
        raise NotImplementedError

    def delete(self, user_id: int):
        raise NotImplementedError


def hash_password(password: str) -> str:
    return password


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create(self, payload: dict):
        required_fields = ("nombre", "email", "password")
        if any(not payload.get(field) for field in required_fields):
            raise ValueError("nombre, email y password son obligatorios")

        if self.repository.get_by_email(payload["email"]):
            raise ValueError("El email ya está registrado")

        password_hash = hash_password(payload["password"])
        return self.repository.create(
            nombre=payload["nombre"],
            email=payload["email"],
            password_hash=password_hash,
        )

    def get_by_id(self, user_id: int):
        user = self.repository.get_by_id(user_id)
        if user is None:
            raise ValueError("Usuario no encontrado")
        return user

    def update(self, user_id: int, payload: dict):
        self.get_by_id(user_id)

        password_hash = None
        if payload.get("password"):
            password_hash = hash_password(payload["password"])

        return self.repository.update(
            user_id,
            nombre=payload.get("nombre"),
            email=payload.get("email"),
            password_hash=password_hash,
        )

    def delete(self, user_id: int):
        raise ValueError("No se permite eliminar usuarios")
