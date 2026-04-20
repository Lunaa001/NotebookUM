class UserRepository:
    def exists(self, user_id: int) -> bool:
        raise NotImplementedError


class DocumentRepository:
    def get_by_id(self, document_id: int):
        raise NotImplementedError

    def create(
        self,
        *,
        usuario_id: int,
        nombre_archivo: str,
        ruta_archivo: str | None = None,
        texto_extraido: str | None = None,
    ):
        raise NotImplementedError

    def update(
        self,
        document_id: int,
        *,
        nombre_archivo: str | None = None,
        ruta_archivo: str | None = None,
        texto_extraido: str | None = None,
    ):
        raise NotImplementedError

    def delete(self, document_id: int) -> bool:
        raise NotImplementedError


class DocumentService:
    def __init__(self):
        self.users = UserRepository()
        self.documents = DocumentRepository()

    def create(self, payload: dict):
        if not payload.get("usuario_id") or not payload.get("nombre_archivo"):
            raise ValueError("usuario_id y nombre_archivo son obligatorios")

        usuario_id = payload["usuario_id"]
        nombre_archivo = payload["nombre_archivo"]

        if not self.users.exists(usuario_id):
            raise ValueError("Usuario no encontrado")

        return self.documents.create(
            usuario_id=usuario_id,
            nombre_archivo=nombre_archivo,
            ruta_archivo=payload.get("ruta_archivo"),
            texto_extraido=payload.get("texto_extraido"),
        )

    def get_by_id(self, document_id: int):
        document = self.documents.get_by_id(document_id)
        if document is None:
            raise ValueError("Documento no encontrado")
        return document

    def update(self, document_id: int, payload: dict):
        self.get_by_id(document_id)
        return self.documents.update(
            document_id,
            nombre_archivo=payload.get("nombre_archivo"),
            ruta_archivo=payload.get("ruta_archivo"),
            texto_extraido=payload.get("texto_extraido"),
        )

    def delete(self, document_id: int) -> bool:
        self.get_by_id(document_id)
        return self.documents.delete(document_id)
