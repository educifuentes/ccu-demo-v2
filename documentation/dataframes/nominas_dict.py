NOMINAS_DATA_DICTIONARY = {
    "local_id": {
        "label": "ID del local",
        "description": "Identificador único del local comercial.",
        "data_type": "texto",
        "data_type_label": "Texto"
    },
    "periodo": {
        "label": "Período",
        "description": "Período de referencia del registro, usualmente expresado como año y trimestre o mes.",
        "data_type": "texto",
        "data_type_label": "Texto"
    },
    "situacion": {
        "label": "Situación del local",
        "description": "Estado operativo del local en el período considerado (por ejemplo, abierto, cerrado, implementado).",
        "data_type": "categórico",
        "data_type_label": "Categoría"
    },
    "schoperas_base": {
        "label": "Schoperas base",
        "description": "Cantidad de schoperas instaladas en el local en el período base.",
        "data_type": "entero",
        "data_type_label": "Número entero"
    },
    "schoperas_delta": {
        "label": "Variación de schoperas",
        "description": "Cambio neto en la cantidad de schoperas respecto del período base.",
        "data_type": "entero",
        "data_type_label": "Número entero"
    },
    "salidas_base": {
        "label": "Salidas base",
        "description": "Cantidad de salidas o puntos de dispensación en el período base.",
        "data_type": "entero",
        "data_type_label": "Número entero"
    },
    "salidas_delta": {
        "label": "Variación de salidas",
        "description": "Cambio neto en la cantidad de salidas respecto del período base.",
        "data_type": "entero",
        "data_type_label": "Número entero"
    },
    "mes_cambio": {
        "label": "Mes de cambio",
        "description": "Mes calendario en que se registró un cambio en la configuración del local.",
        "data_type": "texto",
        "data_type_label": "Texto"
    },
    "motivo": {
        "label": "Motivo del cambio",
        "description": "Razón reportada que explica el cambio en schoperas o salidas.",
        "data_type": "texto",
        "data_type_label": "Texto"
    }
}