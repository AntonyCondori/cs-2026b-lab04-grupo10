workspace "EcoRecicla AQP" "Modelo C4 de la plataforma de recolección de material reciclable" {

    !identifiers hierarchical

    model {
        // Personas
        vecino = person "Vecino" "Ciudadano de Arequipa que separa sus residuos y solicita recojos."
        reciclador = person "Reciclador" "Recolector formalizado que atiende las solicitudes de recojo."
        municipalidad = person "Municipalidad" "Supervisa el impacto ambiental y las métricas de reciclaje."

        // Sistema principal y sus CONTENEDORES (E2)
        ecorecicla = softwareSystem "EcoRecicla AQP" "Plataforma que conecta vecinos con recicladores." {
            
            appVecino = container "App Vecino" "Interfaz web progresiva para que los ciudadanos reporten reciclaje." "PWA / React" "Web Browser"
            appReciclador = container "App Reciclador" "Interfaz web progresiva para gestionar rutas." "PWA / React" "Web Browser"
            api = container "API REST" "Monolito modular que gestiona solicitudes, usuarios y rutas." "Node.js / Express"
            db = container "Base de Datos" "Almacena la información de usuarios, solicitudes y rutas." "PostgreSQL" "Database"
            optimizador = container "Optimizador de Rutas" "Tarea asíncrona para calcular la mejor ruta diaria." "Node.js"
        }

        // Sistemas externos
        mapas = softwareSystem "Servicio de mapas y rutas" "Provee geolocalización y optimización de rutas." "Externo"
        whatsapp = softwareSystem "WhatsApp" "Envía notificaciones y alertas a los usuarios." "Externo"

        // Relaciones hacia los Contenedores (con protocolos)
        vecino -> ecorecicla.appVecino "Solicita el recojo de material reciclable" "HTTPS"
        reciclador -> ecorecicla.appReciclador "Revisa rutas asignadas y confirma recojos" "HTTPS"
        municipalidad -> ecorecicla.api "Consulta reportes de impacto ambiental" "HTTPS/JSON"
        
        // Relaciones Internas entre Contenedores
        ecorecicla.appVecino -> ecorecicla.api "Hace llamadas a" "HTTPS/JSON"
        ecorecicla.appReciclador -> ecorecicla.api "Hace llamadas a" "HTTPS/JSON"
        ecorecicla.api -> ecorecicla.db "Lee y escribe datos" "SQL/TCP"
        ecorecicla.optimizador -> ecorecicla.db "Lee solicitudes y actualiza rutas" "SQL/TCP"
        
        // Relaciones hacia Sistemas Externos
        ecorecicla.optimizador -> mapas "Solicita optimización de rutas" "HTTPS/JSON"
        ecorecicla.api -> whatsapp "Envía notificaciones de estado de recojo" "HTTPS/JSON"
    }

    views {
        systemContext ecorecicla "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autolayout lr
        }

        // Nueva vista agregada para el E2
        container ecorecicla "Contenedores" "Nivel 2: Contenedores de EcoRecicla AQP." {
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
            element "Container" {
                background #438DD5
                color #ffffff
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
        }
    }
}