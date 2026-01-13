CENSOS_DATA_DICTIONARY = {
    "local_id": {
        "label": "ID Local",
        "description": "Identificador único del local comercial.",
        "data_type": "string",
        "data_type_label": "Texto (identificador único del local)"
    },
    "periodo": {
        "label": "Período",
        "description": "Período de reporte asociado al registro.",
        "data_type": "string",
        "data_type_label": "Texto (ej.: 2025-01 o 2025-Q1)"
    },
    "marcas_abenv": {
        "label": "Marcas AB InBev",
        "description": "Disponibilidad de marcas AB InBev en el local.",
        "data_type": "boolean",
        "data_type_label": "Sí / No"
    },
    "marcas_kross": {
        "label": "Marcas Kross",
        "description": "Disponibilidad de marcas Kross en el local.",
        "data_type": "boolean",
        "data_type_label": "Sí / No"
    },
    "marcas_otras": {
        "label": "Otras marcas",
        "description": "Disponibilidad de marcas de otros productores.",
        "data_type": "boolean",
        "data_type_label": "Sí / No"
    },
    "schoperas_ccu": {
        "label": "Schoperas CCU",
        "description": "Número de schoperas CCU instaladas en el local.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "schoperas_otros": {
        "label": "Schoperas de otros proveedores",
        "description": "Número de schoperas de proveedores distintos de CCU.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "salidas_ccu": {
        "label": "Salidas CCU",
        "description": "Número de salidas asociadas a schoperas CCU.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "coolers_total": {
        "label": "Coolers totales",
        "description": "Número total de coolers disponibles en el local.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "salidas_instaladas": {
        "label": "Salidas instaladas",
        "description": "Número de salidas CCU instaladas en el local.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "marcas_salidas_instaladas": {
        "label": "Marcas en salidas instaladas",
        "description": "Marcas asociadas a las salidas CCU instaladas.",
        "data_type": "string",
        "data_type_label": "Texto con múltiples valores"
    },
    "salidas_disponibilizadas": {
        "label": "Salidas disponibilizadas",
        "description": "Número de salidas CCU disponibilizadas en el local.",
        "data_type": "Int64",
        "data_type_label": "Número entero"
    },
    "marcas_salidas_disponibilizadas": {
        "label": "Marcas en salidas disponibilizadas",
        "description": "Marcas CCU disponibilizadas en las salidas del local.",
        "data_type": "string",
        "data_type_label": "Texto con múltiples valores"
    }
}