workspace "EcoRecicla AQP" "Modelo C4 de la plataforma de recolección de material reciclable" {

    !identifiers hierarchical

    model {
        // 1. Personas
        vecino = person "Vecino" "Ciudadano de Arequipa que separa sus residuos y solicita recojos."
        reciclador = person "Reciclador" "Recolector formalizado que atiende las solicitudes de recojo."
        municipalidad = person "Municipalidad" "Supervisa el impacto ambiental y las métricas de reciclaje."

        // 2. Sistema principal
        ecorecicla = softwareSystem "EcoRecicla AQP" "Plataforma que conecta vecinos con recicladores para optimizar el recojo de residuos." {
            // Nota: Aquí se agregarán los contenedores en el E2
        }

        // 3. Sistemas externos
        mapas = softwareSystem "Servicio de mapas y rutas" "Provee geolocalización y optimización de rutas de recojo." "Externo"
        whatsapp = softwareSystem "WhatsApp" "Envía notificaciones y alertas a los usuarios." "Externo"

        // 4. Relaciones (Nivel 1: Contexto)
        vecino -> ecorecicla "Solicita el recojo de material reciclable"
        reciclador -> ecorecicla "Revisa rutas asignadas y confirma recojos"
        municipalidad -> ecorecicla "Consulta reportes de impacto ambiental"
        
        ecorecicla -> mapas "Solicita optimización de rutas"
        ecorecicla -> whatsapp "Envía notificaciones de estado de recojo"
    }

    views {
        systemContext ecorecicla "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autolayout lr
        }

        styles {
            element "Person" {
                background #08427B
                color #ffffff
                shape person
            }
            element "Software System" {
                background #1168BD
                color #ffffff
            }
            element "Externo" {
                background #999999
                color #ffffff
            }
        }
    }
}