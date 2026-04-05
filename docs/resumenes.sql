-- Tabla: resumenes
CREATE TABLE resumenes (
    id SERIAL PRIMARY KEY,
    documento_id INT NOT NULL,
    contenido TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_documento
        FOREIGN KEY (documento_id)
        REFERENCES documentos(id)
        ON DELETE CASCADE
);