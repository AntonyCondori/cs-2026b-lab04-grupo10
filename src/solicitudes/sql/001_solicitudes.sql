CREATE TABLE IF NOT EXISTS solicitudes_recojo (
    distrito_id text NOT NULL,
    solicitud_id text NOT NULL,
    vecino_id text NOT NULL,
    direccion jsonb NOT NULL,
    detalles jsonb NOT NULL,
    estado text NOT NULL CHECK (estado IN (
        'PENDIENTE', 'ASIGNADA', 'RECOGIDA', 'PESADA', 'PUNTOS_ACREDITADOS', 'RECHAZADA'
    )),
    motivo_rechazo text,
    fecha_creacion timestamp NOT NULL,
    reciclador_id text,
    peso_real_kg double precision,
    puntos integer CHECK (puntos >= 0),
    PRIMARY KEY (distrito_id, solicitud_id)
);

CREATE TABLE IF NOT EXISTS confirmaciones_recojo (
    distrito_id text NOT NULL,
    solicitud_id text NOT NULL,
    clave text NOT NULL CHECK (length(trim(clave)) > 0),
    peso_kg double precision NOT NULL CHECK (peso_kg > 0 AND peso_kg < 'Infinity'),
    PRIMARY KEY (distrito_id, solicitud_id),
    UNIQUE (distrito_id, clave),
    FOREIGN KEY (distrito_id, solicitud_id) REFERENCES solicitudes_recojo (distrito_id, solicitud_id)
);

CREATE TABLE IF NOT EXISTS abonos_recojo (
    distrito_id text NOT NULL,
    solicitud_id text NOT NULL,
    puntos integer NOT NULL CHECK (puntos >= 0),
    PRIMARY KEY (distrito_id, solicitud_id),
    FOREIGN KEY (distrito_id, solicitud_id) REFERENCES confirmaciones_recojo (distrito_id, solicitud_id)
);
