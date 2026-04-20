class DocumentRepository:
    def exists(self, document_id: int) -> bool:
        raise NotImplementedError


class SummaryRepository:
    def get_by_id(self, summary_id: int):
        raise NotImplementedError

    def create(self, *, documento_id: int, contenido: str):
        raise NotImplementedError

    def update(self, summary_id: int, *, contenido: str):
        raise NotImplementedError

    def delete(self, summary_id: int) -> bool:
        raise NotImplementedError


class SummaryService:
    def __init__(self):
        self.documents = DocumentRepository()
        self.summaries = SummaryRepository()

    def create(self, payload: dict):
        if not payload.get("documento_id") or not payload.get("contenido"):
            raise ValueError("documento_id y contenido son obligatorios")

        documento_id = payload["documento_id"]
        contenido = payload["contenido"]

        if not self.documents.exists(documento_id):
            raise ValueError("Documento no encontrado")

        return self.summaries.create(documento_id=documento_id, contenido=contenido)

    def get_by_id(self, summary_id: int):
        summary = self.summaries.get_by_id(summary_id)
        if summary is None:
            raise ValueError("Resumen no encontrado")
        return summary

    def update(self, summary_id: int, payload: dict):
        self.get_by_id(summary_id)
        return self.summaries.update(summary_id, contenido=payload.get("contenido"))

    def delete(self, summary_id: int) -> bool:
        self.get_by_id(summary_id)
        return self.summaries.delete(summary_id)
