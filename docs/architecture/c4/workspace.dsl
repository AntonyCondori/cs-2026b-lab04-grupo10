workspace "EcoRecicla AQP" "Modelo C4 de la plataforma de recolección de material reciclable" {

    !identifiers hierarchical

    model {
        // 1. Personas
        vecino = person "Vecino" "Ciudadano de Arequipa que separa sus residuos y solicita recojos."
        reciclador = person "Reciclador" "Recolector formalizado que atiende las solicitudes de recojo."
        municipalidad = person "Municipalidad" "Supervisa el impacto ambiental y las métricas de reciclaje."

        // 2. Sistemas externos
        mapas = softwareSystem "Servicio de mapas y rutas" "Provee geolocalización y optimización." "Externo"
        whatsapp = softwareSystem "WhatsApp" "Envía notificaciones a los usuarios." "Externo"

        // 3. Sistema principal y Contenedores
        ecorecicla = softwareSystem "EcoRecicla AQP" "Plataforma que conecta vecinos con recicladores." {
            
            appVecino = container "App Vecino" "Interfaz web progresiva para reportar reciclaje." "PWA / React" "Web Browser"
            appReciclador = container "App Reciclador" "Interfaz web progresiva para gestionar rutas. [QA-05] [QA-06]" "PWA / React" "Web Browser"
            db = container "Base de Datos" "Almacena usuarios, solicitudes, puntos y rutas. [QA-03] [QA-06]" "PostgreSQL" "Database"
            optimizador = container "Optimizador de Rutas" "Tarea asíncrona para calcular la mejor ruta. [QA-06]" "Node.js Cron"
            
            // CONTENEDOR PRINCIPAL Y SUS COMPONENTES (E3)
            api = container "API REST" "Monolito modular que gestiona todo el dominio del sistema. [QA-01] [QA-03]" "Node.js / Express" {
                reportes = component "Módulo Reportes" "Consultas públicas de solicitudes, rutas y puntos. [QA-03]" "Node.js Express Router"
                rutas = component "Módulo Rutas" "Gestión y asignación de rutas. [QA-06]" "Node.js Express Router"
                solicitudes = component "Módulo Solicitudes" "Manejo de recojos y adaptadores externos; confirmación sin duplicados. [QA-04]" "Node.js Express Router"
                puntos = component "Módulo Puntos y Canjes" "Acreditación de puntos por material; reglas registradas en arranque.py (Strategy, Factory, Decorator). [QA-01] [QA-02]" "Node.js Express Router"
                identidad = component "Módulo Identidad y Distritos" "Gestión de usuarios y validación geográfica base; base del concepto de distrito. [QA-02] [QA-03]" "Node.js Express Router"
            }
        }

        // 4. Relaciones de Personas hacia Contenedores
        vecino -> ecorecicla.appVecino "Solicita recojos" "HTTPS"
        reciclador -> ecorecicla.appReciclador "Revisa rutas asignadas" "HTTPS"
        municipalidad -> ecorecicla.api.reportes "Consulta reportes generales" "HTTPS/JSON"
        
        // 5. Relaciones desde las Apps hacia los Componentes
        ecorecicla.appVecino -> ecorecicla.api.identidad "Inicia sesión" "HTTPS/JSON"
        ecorecicla.appVecino -> ecorecicla.api.solicitudes "Registra solicitudes" "HTTPS/JSON"
        ecorecicla.appReciclador -> ecorecicla.api.identidad "Inicia sesión" "HTTPS/JSON"
        ecorecicla.appReciclador -> ecorecicla.api.rutas "Consulta rutas" "HTTPS/JSON"
        ecorecicla.appReciclador -> ecorecicla.api.solicitudes "Actualiza estado" "HTTPS/JSON"

        // 6. Relaciones Internas entre Componentes
        ecorecicla.api.reportes -> ecorecicla.api.solicitudes "Consulta pública de solicitudes"
        ecorecicla.api.reportes -> ecorecicla.api.rutas "Consulta pública de rutas"
        ecorecicla.api.reportes -> ecorecicla.api.puntos "Consulta pública de puntos"
        ecorecicla.api.rutas -> ecorecicla.api.solicitudes "Consulta pendientes y asigna solicitud"
        ecorecicla.api.solicitudes -> ecorecicla.api.identidad "Valida referencias"
        ecorecicla.api.solicitudes -> ecorecicla.api.puntos "Acredita puntos"
        ecorecicla.api.puntos -> ecorecicla.api.identidad "Consulta distrito"
        
        // 7. Relaciones de Componentes hacia la Base de Datos
        ecorecicla.api.reportes -> ecorecicla.db "Lee" "SQL/TCP"
        ecorecicla.api.rutas -> ecorecicla.db "Lee y escribe" "SQL/TCP"
        ecorecicla.api.solicitudes -> ecorecicla.db "Lee y escribe" "SQL/TCP"
        ecorecicla.api.puntos -> ecorecicla.db "Lee y escribe" "SQL/TCP"
        ecorecicla.api.identidad -> ecorecicla.db "Lee y escribe" "SQL/TCP"
        ecorecicla.optimizador -> ecorecicla.db "Lee solicitudes y actualiza rutas" "SQL/TCP"

        // 8. Relaciones hacia Sistemas Externos
        ecorecicla.api.solicitudes -> mapas "Consulta la ubicación de la dirección" "HTTPS/JSON"
        ecorecicla.api.solicitudes -> whatsapp "Envía notificaciones del recojo" "HTTPS/JSON"
        ecorecicla.optimizador -> mapas "Solicita optimización de rutas" "HTTPS/JSON"
        // 9. Despliegue (E5): un solo servidor en la nube (ADR-001, R-03)
        produccion = deploymentEnvironment "Producción" {
            deploymentNode "Dispositivo del usuario" "Celular o PC de vecinos y recicladores" "Android / navegador web" {
                containerInstance ecorecicla.appVecino
                containerInstance ecorecicla.appReciclador
            }
            deploymentNode "Servidor en la nube" "Un solo servidor, sin alta disponibilidad (ADR-001); tamaño por cotizar (R-03)" "Ubuntu Server LTS" {
                infrastructureNode "Nginx" "Proxy inverso y terminación HTTPS" "Nginx"
                deploymentNode "Entorno de ejecución" "" "Node.js" {
                    containerInstance ecorecicla.api
                    containerInstance ecorecicla.optimizador
                }
                deploymentNode "Motor de base de datos" "" "PostgreSQL" {
                    containerInstance ecorecicla.db
                }
            }
        }
    }

    views {
        systemContext ecorecicla "Contexto" "Nivel 1: EcoRecicla AQP y su entorno." {
            include *
            autolayout lr
        }
        
        container ecorecicla "Contenedores" "Nivel 2: Contenedores de EcoRecicla AQP." {
            include *
            autolayout lr
        }
        
        component ecorecicla.api "Componentes" "Nivel 3: Módulos internos de la API REST." {
            include *
            autolayout lr
        }

        dynamic ecorecicla.api "SolicitarRecojo" "Dinámico: el vecino solicita un recojo (HU-01, camino exitoso)." {
            ecorecicla.appVecino -> ecorecicla.api.solicitudes "POST /solicitudes (dirección y residuos)"
            ecorecicla.api.solicitudes -> mapas "Geocodifica la dirección"
            ecorecicla.api.solicitudes -> ecorecicla.db "Guarda la solicitud como PENDIENTE"
            ecorecicla.api.solicitudes -> ecorecicla.appVecino "201 Created: confirmación del recojo"
            autolayout lr
        }

        deployment ecorecicla produccion "Despliegue" "Despliegue en producción (MVP): un solo servidor en la nube." {
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
            element "Component" {
                background #85BBF0
                color #000000
            }
            element "Database" {
                shape cylinder
            }
            element "Web Browser" {
                shape WebBrowser
            }
            element "Infrastructure Node" {
                background #ffffff
                color #000000
            }
        }
    }
}