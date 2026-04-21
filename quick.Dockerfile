FROM notebookum:1.0.0
USER root
COPY --chown=appuser:appuser . .
USER appuser