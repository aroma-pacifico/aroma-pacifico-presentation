# Guion de la sustentación

| Campo | Valor |
|---|---|
| Estado | Guion de ensayo. El tiempo de cada diapositiva es su texto leído a 130 palabras por minuto; el ensayo completo lo confirma. |
| Issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Presentación | `deck/aroma-pacifico-sustentacion.pptx` y `.pdf`: 40 diapositivas, 1 a 39 de exposición y la 40 de anexo con los enlaces a cada diagrama |
| Duración | 19:35 de exposición, dentro de la meta de 18 a 20 minutos |
| Fuente | Generado por `deck/build_deck.py` desde `deck/content.yaml`; las notas del orador del PPTX tienen el mismo texto. No se edita a mano. |

El guion está escrito para decirse en voz alta, en frases cortas, a unas 130 palabras por minuto. Cada presentador adapta la redacción; las cifras y las referencias son la parte fija. Toda cifra es del enunciado del caso, aritmética sobre una de ellas o una meta de diseño: se dice «meta de diseño» y nunca «medido». La fuente de cada diapositiva queda al final de su texto y en las notas del orador, no en la diapositiva.

En la portada, Esteban lee el título y pasa a la diapositiva del equipo, donde cada presentador dice su nombre y su rol en el orden de la exposición. Las diapositivas de diagrama completo duran poco: el presentador señala tres zonas y sigue; el detalle queda en el anexo para las preguntas.

## Reparto y tiempos

| Bloque | Presenta | Diapositivas | Tiempo |
|---|---|---|---|
| 1 | Esteban Gaviria Zambrano (SR1) | 1 a 12 | 6:15 |
| 2 | Karen Valeria Jurado Calpa (JR1) | 13 a 19 | 3:45 |
| 3 | Jeanpaul Atkinson Vidales Gallego (SR2) | 20 a 26 | 3:35 |
| 4 | César Augusto Jiménez Reina (JR2) | 27 a 34 | 3:50 |
| 5 | Esteban Gaviria Zambrano (SR1) | 35 a 39 | 2:10 |
| Total | SR1 8:25, JR1 3:45, SR2 3:35, JR2 3:50 | 1 a 39 | 19:35 |

## Guion por diapositiva

### Bloque 1: Esteban Gaviria Zambrano (SR1), diapositivas 1 a 12, 6:15

**Diapositiva 1 (0:10). Trazabilidad del café de la finca al puerto, lista para operar**

Buenos días. Somos el equipo que propone diseñar, codificar y entregar la actualización 2026 del piloto de trazabilidad de café de Aroma Pacífico.

**Diapositiva 2 (0:30). El equipo**

Cada integrante dice su nombre, su rol y la parte que presenta: Esteban Gaviria Zambrano, Senior DevOps, el caso, la arquitectura y el gobierno, y al final los costos; Karen Valeria Jurado Calpa, Junior DevOps, red, conectividad y seguridad; Jeanpaul Atkinson Vidales Gallego, Senior DevOps, las cargas: finca, drones, inferencia, saco y observabilidad; César Augusto Jiménez Reina, Junior DevOps, la infraestructura como código y el plan de 100 horas.

**Diapositiva 3 (0:30). 200 fincas sin señal confiable necesitan una trazabilidad que no dependa de ella**

El piloto de 2020 rastreaba el café desde la finca hasta el comprador, pero nunca se desplegó, y su supuesto central ya no se cumple: suponía señal en la mayoría de las fincas.
En 2026 son 200 fincas en tres departamentos, tres centros de acopio, 60 transportadores y la entrega en Buenaventura. Nuestra propuesta parte de un principio: cada flujo funciona aunque no haya señal.

Fuente: Enunciado del caso, «Contexto», «Qué se actualiza» y «Cifras del piloto».

**Diapositiva 4 (0:50). Nos comprometemos con metas medibles, no con promesas**

Estas son las metas con las que nos comprometemos. Dos SLO: el 95 por ciento de las alertas llega al caficultor en 300 segundos y el 99,5 por ciento de las consultas del saco responde sin error, ambos en 28 días móviles.
Del caso vienen la alerta en menos de 5 minutos, el búfer de 24 horas, la retención de 5 años, el RPO de 15 minutos y el RTO de 4 horas. La IaC ocupa 98 de las 100 horas y el piloto cuesta 2.707 dólares en un mes normal y 10.639 en cosecha. Todas son metas de diseño, con su indicador definido.

Fuente: Observabilidad, ASM-224 y ASM-225 · Enunciado del caso · Plan de 100 horas · Costos del piloto, sección 1.

**Diapositiva 5 (0:35). Las reglas de operación del cliente definen el diseño**

El cliente fija reglas que no negociamos: una sola visita a la finca, poca inversión del caficultor, una app de pocas pantallas y un dron gobernado. En lo técnico: un nodo autónomo en energía, un patrón que escala a 1.000 fincas sin redireccionar, ningún cambio productivo en el día de una semana de cosecha y una IaC acotada a 100 horas. Cada decisión que sigue responde a una de estas reglas.

Fuente: Enunciado del caso, «Restricciones», «Automatización y cambio» y «Épica 6».

**Diapositiva 6 (0:25). De 2020 conservamos ocho requisitos y reemplazamos lo que dejó de ser cierto**

No copiamos la arquitectura de 2020, como pide el caso. De 18 elementos, conservamos 8 requisitos que siguen vigentes, reemplazamos 4 supuestos de conectividad que ya no se cumplen y retiramos 6 elementos, como los precios y el manual de 2020. La trazabilidad de cada uno está en el anexo A04.

Fuente: Arquitectura, sección 13 · legacy-2020.md · legacy/legacy-2020.svg.

**Diapositiva 7 (0:40). Dimensionamos con las cifras del caso, de hoy y a cinco años**

Dimensionamos con las cifras del caso. Al día entran 1.200 lecturas de cultivo y, en cosecha, 2.400 de secado; 7.200 posiciones de transportadores y hasta 1.200 sacos. La consulta del saco tiene picos de 30 por minuto, y en un mes de cosecha hay 108.270 invocaciones de funciones y solo 420 llamadas al modelo.
A cinco años son 13 millones de posiciones y 2,19 millones de sacos. Y a 1.000 fincas la ingesta sube a 18.000 lecturas diarias, 0,21 por segundo: el patrón no cambia.

Fuente: Monitoreo de finca, sección 3 · Saco y viaje, sección 8 · Plan de direccionamiento, sección 6 · Costos del piloto, sección 6.4.

**Diapositiva 8 (0:45). Elegimos AWS en us-east-1 y dejamos Azure preparada sin duplicar la plataforma**

La nube principal es AWS, en una sola región, us-east-1. Los criterios: que funciones, almacenamiento e inferencia administrada vivan en la misma región, para decir a qué país y a qué región salen los objetos; que las 28 reglas IaC del equipo ya estén escritas para AWS; y no duplicar la plataforma.
sa-east-1 no permite nombrar la región de la inferencia de visión, y Azure o GCP como principal exigiría reescribir las reglas dentro de las 100 horas. Azure queda preparada con tres propiedades: interfaces neutrales, datos en formato abierto y un destino de exportación declarado, sin desplegar nada.

Fuente: ADR-001, contexto, decisión y alternativas.

**Diapositiva 9 (0:20). Una plataforma por eventos en una región, con el borde diseñado para operar sin señal**

La arquitectura objetivo cabe en cuatro ideas. Una organización con cinco cuentas y un /16 por ambiente. Un borde autónomo que guarda y libera al confirmar. Cómputo solo por eventos, sin servidores esperando. Y datos cifrados con llaves propias por almacén, guardados cinco años. Veamos el diagrama completo.

Fuente: Arquitectura, secciones 1, 4, 5 y 7 · complete/architecture.svg.

**Diapositiva 10 (0:30). La arquitectura completa: borde, organización AWS y cajas D01 a D13**

Arriba, el borde: fincas, centros de acopio, la operación contratada de drones y el transporte con la consulta pública. Abajo, la organización AWS, con la IaC a la izquierda y la cuenta de producción a la derecha. Las insignias D01 a D13 marcan lo que construye el código. Al pie, los dos flujos de negocio: la custodia del saco y de la plaga a la fumigación.

Fuente: aroma-pacifico-diagrams, complete/architecture.svg.

**Diapositiva 11 (0:15). En el borde, cada actor guarda localmente y publica al recuperar la señal**

En el detalle del borde se ve la regla común: el nodo de finca, la estación de tierra y el teléfono del transportador guardan cifrado y liberan solo al confirmar la recepción.

Fuente: aroma-pacifico-diagrams, complete/architecture.svg (detalle).

**Diapositiva 12 (0:45). Gobernamos desde la raíz: políticas, etiquetas, presupuestos y auditoría**

El gobierno se aplica desde la raíz: siete políticas de control de servicios, entre ellas solo us-east-1, sin credenciales de larga duración y cambios de producción solo por el pipeline. La política de etiquetas fija ocho claves y cinco reparten el costo por fincas, drones, acopio, viajes y ambientes.
Los presupuestos son de 650 dólares en mes normal y 700 en cosecha, con alertas al 80 y al 100 por ciento, y el trail de la organización guarda cinco años los cuatro eventos que el caso pide auditar. Con esto Karen continúa con la red.

Fuente: Zona de aterrizaje, secciones 3 a 7 · accounts/landing-zone.svg.

*Transición: Esteban cede la palabra a Karen, que continúa en la diapositiva 13.*

### Bloque 2: Karen Valeria Jurado Calpa (JR1), diapositivas 13 a 19, 3:45

**Diapositiva 13 (0:35). Identidad, no dirección: la red crece de 200 a 1.000 fincas sin redireccionar**

La regla de la red es identidad, no dirección. Fincas, teléfonos y drones no tienen dirección en la nube; se autentican con un certificado o un token. Por eso crecer de 200 a 1.000 fincas suma identidades, no subredes.
Cada ambiente tiene su /16: 10.80 desarrollo, 10.81 pruebas y 10.82 producción, sin tocar el 10.40 barra 13 de los centros. Hay reservas para AWS y un bloque para Azure, que no se despliega.

Fuente: Plan de direccionamiento, secciones 2 a 6 · network/addressing-plan.svg.

**Diapositiva 14 (0:30). Cada flujo tiene protocolo, búfer y conducta sin señal**

Este es el diseño de conectividad, en el cuerpo de la propuesta y no en un anexo. La finca publica MQTT sobre TLS con certificado X.509; la finca sin cobertura usa el mismo nodo con portador satelital; el dron baja sus objetos por el centro o por la cabecera municipal; el transportador publica cada 5 minutos con bandeja cifrada; y el puerto solo registra la entrega.

Fuente: aroma-pacifico-diagrams, network/connectivity.svg · Conectividad, secciones 2 a 11.

**Diapositiva 15 (0:35). Sin señal no se pierde nada: cada actor guarda y libera al confirmar**

Sin señal no se pierde nada. El nodo guarda hasta 24 horas cifradas; al volver publica primero una lectura en vivo y luego vacía el búfer. La finca sin cobertura usa el mismo nodo por satélite. La app del transportador guarda 7 días y nunca descarta un evento de custodia. Y la misión del dron viaja precargada.
En la nube, cada lectura se deduplica por nodo y hora, así que un reintento no duplica alertas.

Fuente: Conectividad, secciones 4.3, 6, 7 y 8 · ASM-073 a ASM-079 · network/no-signal-sequence.svg.

**Diapositiva 16 (0:20). La alerta cabe en 300 segundos: 210 de presupuesto y 90 de margen**

Este es el presupuesto de latencia en siete saltos, del sensor al teléfono, cada uno con su meta: 210 segundos de meta y 90 de margen dentro de los 300 del caso. El búfer y la reconexión están en el anexo A07.

Fuente: aroma-pacifico-architecture, connectivity.md, sección 8.2.

**Diapositiva 17 (0:45). Un solo patrón de LAN para los tres centros, con firewall y sin NAT**

En los centros de acopio, un solo patrón sirve a los tres departamentos con dos parámetros: la clave del centro y el segundo octeto. Siete zonas con su SSID; la de visitantes no llega a logística ni a gerencia. La WAN es de 100 megabits con dos túneles IPsec y respaldo celular; el pico pide 68 y planeamos 90. En Buenaventura no instalamos nada. Hay un firewall en cada centro y uno de nube, sin NAT gateway ni appliance: llegamos a AWS por endpoints privados y eso ahorra 10.856 dólares netos al año.

Fuente: aroma-pacifico-architecture, collection-center-network.md, connectivity.md y firewall-policy.md.

**Diapositiva 18 (0:20). El centro de acopio: zonas segmentadas detrás de un firewall perimetral**

Cada zona es un /24 con su SSID detrás del firewall perimetral. En el diagrama completo, cada flecha verde es una regla permitida con su ID y cada roja una denegación. El patrón se repite tres veces sin redibujar.

Fuente: aroma-pacifico-diagrams, network/collection-center.svg.

**Diapositiva 19 (0:40). Identidades separadas, MFA donde hay riesgo y revocación inmediata**

Cada rol del caso tiene su identidad con mínimo privilegio, y el MFA es obligatorio para el operario de acopio, el operador de drones, el de plataforma y el agrónomo, que además se reautentica para autorizar una fumigación.
Ocho llaves KMS con rotación cifran cada clase de datos. Un nodo o un dron perdido pierde su certificado y su conexión; la meta es completar la baja en 4 horas desde el reporte. El comprador solo ve cuatro grupos de datos. Jeanpaul sigue con las cargas.

Fuente: Seguridad e identidad, secciones 2 a 10 · ASM-098 · security/identity-and-access.svg · security/revocation-sequence.svg.

*Transición: Karen cede la palabra a Jeanpaul, que continúa en la diapositiva 20.*

### Bloque 3: Jeanpaul Atkinson Vidales Gallego (SR2), diapositivas 20 a 26, 3:35

**Diapositiva 20 (0:30). Del sensor al teléfono del caficultor en siete saltos y menos de 5 minutos**

El monitoreo de finca recorre siete saltos, cada uno con su meta: suman 210 segundos y dejan 90 de margen dentro de los 300 del caso. La función evalúa contra los umbrales que publica la Federación, que son datos y no código.
Abrimos una alerta por episodio, no por lectura, y la entregamos por SMS y push. El historial queda cinco años.

Fuente: Monitoreo de finca, secciones 3 a 7 · Conectividad, sección 8 · flows/farm-monitoring-sequence.svg.

**Diapositiva 21 (0:35). El modo combinado es el único que cubre los cinco servicios del dron**

El caso pide cinco servicios y ninguno reemplaza a otro. El modo área delimita el lote y estima la cosecha; el modo precisión confirma la alerta, fumiga el foco y verifica el mismo lote. Solo el combinado cubre los cinco.
El cambio de modo son dos eventos persistidos y solo un foco confirmado lleva a una orden. Vuela un operador certificado contratado y autoriza un agrónomo con MFA: es el ADR-002.

Fuente: ADR-002, modo de vuelo y gobierno del dron · Servicio de drones, secciones 3 a 6.

**Diapositiva 22 (0:15). La orden de fumigación solo sale con autorización humana y MFA**

En el detalle, la fase de autorización: el caso confirmado crea un borrador, el agrónomo lo revisa y lo autoriza con MFA, y la plataforma guarda quién autorizó, la ventana y el operador.

Fuente: aroma-pacifico-diagrams, flows/drone-fumigation-sequence.svg, pasos 19 a 21.

**Diapositiva 23 (0:40). Un orquestador por eventos y cuatro funciones; el modelo solo al abrir una alerta**

Un orquestador por eventos coordina las capacidades del dron sin acoplarlas: el objeto persistido dispara un pipe de EventBridge, una regla por tipo lo envía a su cola y cada cola tiene su cola de fallidos; es el ADR-004. Si una invocación falla, el objeto se queda y el caso no cambia. Son cuatro funciones, una por disparador. En un mes de cosecha hay 108.270 invocaciones, pero solo 420 llegan al modelo, porque solo se llama al abrir una alerta: 5,21 dólares. Una foto con una persona no se envía.

Fuente: aroma-pacifico-architecture, adr/adr-004 e inference-functions.md.

**Diapositiva 24 (0:35). El saco se rastrea en siete estados y el comprador solo ve lo que le corresponde**

El saco pasa por siete estados, de en preparación a entregado en puerto, aceptado o rechazado. Cada evento guarda fecha, hora y responsable en un registro de solo agregar, con RPO de 15 minutos.
El código es aleatorio y no revela la cédula. La consulta pública lee una vista separada, con RTO de 4 horas, y el comprador ve solo origen, fechas, estado y secado. Los siete estados y sus responsables están en el anexo A17.

Fuente: Saco y viaje, secciones 2 a 8 · flows/sack-and-trip-sequence.svg · flows/sack-states.svg.

**Diapositiva 25 (0:30). Tres caminos de datos distintos, cada uno con su almacén correcto**

Los tres caminos de datos que pide el caso son distintos a propósito. La telemetría entra por MQTT a IoT Core y termina en DynamoDB. La posición entra por HTTPS a la API. Los objetos del dron suben a S3 por la VPN del centro o con una URL firmada desde la cabecera municipal. Los eventos del saco y las órdenes van a la base transaccional.

Fuente: Conectividad, secciones 4, 6 y 7 · data-paths/data-paths.md · Automatización y pipelines, secciones 6 y 7.

**Diapositiva 26 (0:30). Dos SLO medibles y las cinco detecciones del caso, en dos tableros**

Observamos lo que el caso pide: ingesta, aplicaciones, bases, los tres enlaces WAN y la llegada de objetos de vuelo. Dos SLO con su SLI: la entrega de la alerta y la disponibilidad de la consulta del saco.
Las cinco detecciones del caso tienen su alarma, y hay dos tableros, operativo y de costos, partidos por etiquetas. César sigue con la infraestructura como código.

Fuente: Observabilidad, secciones 2 a 6 · docs/dashboards.

*Transición: Jeanpaul cede la palabra a César, que continúa en la diapositiva 27.*

### Bloque 4: César Augusto Jiménez Reina (JR2), diapositivas 27 a 34, 3:50

**Diapositiva 27 (0:30). La IaC cabe en 100 horas porque construye un ambiente patrón y nada más**

La infraestructura como código cabe en 100 horas porque construye lo que el caso cuenta: módulos, variables, estado remoto y un plan ejecutable de un ambiente patrón. Elegimos Terraform porque nuestras 28 reglas están escritas para él. El estado vive en un bucket cifrado y versionado por ambiente, con bloqueo nativo. Lo que queda fuera es deliberado y está escrito en el ADR-003.

Fuente: ADR-003 · Plan de 100 horas, sección 2.

**Diapositiva 28 (0:25). Trece cajas, trece tareas: el código coincide con el diagrama**

Cada caja es una tarea del plan y una ruta del repositorio. De D01 a D10 son repositorio, estado, variables y módulos. D11, D13 y D12 forman la cadena del plan revisable: la CI produce un plan guardado, se valida con evidencia y el CD lo aplica solo con aprobación humana.

Fuente: aroma-pacifico-diagrams, complete/architecture-iac.svg.

**Diapositiva 29 (0:30). Ocho módulos públicos, versionados por etiqueta, uno por caja**

Este es el catálogo del repositorio público de módulos: ocho módulos, cada uno con su caja y la etiqueta en que se publicó, de la v0.1.0 a la v0.5.0. Ninguno declara proveedor, backend ni cuentas, porque el repositorio es público, y tienen 131 pruebas en modo plan en 8 suites. Los stacks los consumen por etiqueta, así que subir de versión es un cambio revisado.

Fuente: aroma-pacifico-terraform-modules: etiquetas v0.1.0 a v0.5.0, README y tests de cada módulo · pc-iac-015.

**Diapositiva 30 (0:35). Cuatro stacks en orden de dependencia y tres ambientes con la misma receta**

La infraestructura tiene cuatro stacks, uno por dominio, en orden de dependencia: estado, red, seguridad y cargas. Los tres ambientes, dev, qa y pdn, usan los mismos módulos y las mismas etiquetas; cambian solo su archivo de variables, su backend y su CIDR.
El plan de extremo a extremo de qa corre contra el emulador Floci, los cuatro stacks en orden, y valida que no haya secretos en la historia ni en el plan.

Fuente: aroma-pacifico-infrastructure: stacks/, environments/, scripts/plan-all.sh, docs/b13-final-validation.md · ADR-003.

**Diapositiva 31 (0:25). Cada pull request pasa trece chequeos y llega a un plan con su costo**

Así entra un cambio. El pull request pasa el escaneo de secretos, las compuertas de cada stack, el plan contra Floci e Infracost, que publica el costo antes, después y la diferencia junto al plan. Son 13 chequeos por pull request de infraestructura y 29 en el de módulos. Al fusionar, un módulo nuevo se publica por etiqueta.

Fuente: aroma-pacifico-infrastructure: infrastructure-ci.yml, floci-plan.yml, infracost.yml, pr-conventions.yml · pc-iac-027 · pc-iac-028.

**Diapositiva 32 (0:35). Producción aplica solo el plan aprobado, y volver atrás pasa por la misma compuerta**

Subir la infraestructura sigue la promoción dev, qa y pdn. Para producción se publica el plan, el delta de costo y la huella del plan, y otra persona de la lista de aprobadores aprueba exactamente esa huella. El pipeline rechaza la ventana de cosecha salvo un incidente y solo aplica el plan aprobado. Volver atrás es un revert y una nueva promoción; bajar un ambiente va en orden inverso y las tablas con datos tienen prevent_destroy.

Fuente: aroma-pacifico-architecture, automation-and-pipelines.md.

**Diapositiva 33 (0:20). 98 horas en 19 partes, repartidas por rol y por semana**

El plan reparte 98 horas en 19 partes. SR1 lleva 27, SR2 26, JR1 22 y JR2 23. Seis tareas se dividen en módulo y cableado, ninguna pasa de 10 horas y nadie pasa de 25 por semana ni de 5 por día. Quedan 2 horas de reserva.

Fuente: Plan de 100 horas, secciones 4.1 y 6.5.

**Diapositiva 34 (0:30). La ruta crítica dura 38 horas y termina el día 8 de 10**

La ruta crítica tiene dos cadenas de 38 horas que comparten B01, B06a, B03 y B04b; una sigue por B09b, B07b y B12, y la otra por B08 y B05, y ambas cierran en B13. El plan termina en la hora 38 de 50, el día 8, con 12 horas de colchón, y usa el 49 por ciento de la capacidad. Esteban cierra con los costos.

Fuente: Plan de 100 horas, secciones 6.2, 6.4 y 6.5.

*Transición: César cede la palabra a Esteban, que continúa en la diapositiva 35.*

### Bloque 5: Esteban Gaviria Zambrano (SR1), diapositivas 35 a 39, 2:10

**Diapositiva 35 (0:30). El piloto cuesta USD 2.707 en un mes normal y USD 10.639 en cosecha**

El piloto cuesta 2.707 dólares en un mes normal y 10.639 en un mes de cosecha, con 82.550 de inversión inicial. La nube es la parte menor: 559 y 574 dólares, bajo los topes de 650 y 700. Cada finca cuesta 370 dólares de hardware una vez y 4,60 al mes, y la inferencia de un mes de cosecha, 5,21.

Fuente: Costos del piloto, secciones 1, 3, 5, 6 y 7 · ASM-230, ASM-231, ASM-250.

**Diapositiva 36 (0:25). La cosecha la encarece el dron, no la nube: AWS sube solo USD 14,81**

A la izquierda, el costo por dominio: lo que dispara la cosecha es la campaña de dron, que pasa de 583 a 8.500 dólares. A la derecha, la nube por servicio: pesa la red privada, con el resolver, el Transit Gateway y las VPN. La cosecha solo sube la nube 14,81 dólares, por los SMS y la inferencia.

Fuente: Costos del piloto, secciones 1, 3.2 y 7.1 · ASM-230 a ASM-237.

**Diapositiva 37 (0:35). Seis decisiones ahorran USD 47.533 al año y evitan USD 230.000 de inversión**

Seis decisiones bajan el costo: endpoints en vez de Network Firewall y NAT, CloudFront en vez de un balanceador, el modelo solo al abrir una alerta, hardware dual con satélite solo sin señal, drones contratados y DynamoDB bajo demanda. Suman 47.533 dólares al año y 230.000 de inversión evitada.
Y el costo no se descuida después: Infracost publica el costo antes, después y la diferencia en cada pull request y en la aprobación de producción.

Fuente: Costos del piloto, secciones 1, 2 y 9 · ASM-251 · pc-iac-027.

**Diapositiva 38 (0:20). Por qué esta propuesta**

Por qué esta propuesta: funciona sin señal, gobierna los drones con autorización humana, entrega código que coincide con el diagrama dentro de las 100 horas y mantiene el costo bajo control desde el diseño hasta cada pull request.

Fuente: Síntesis de la propuesta.

**Diapositiva 39 (0:20). Gracias**

Gracias. El código QR lleva al sitio de Aroma Pacífico, con la arquitectura, cada diagrama en alta resolución, la IaC, los costos y el sistema de diseño. Recibimos sus preguntas; el anexo tiene cada diagrama completo y sus detalles.

## Anexo para preguntas

Después del cierre viene una sola diapositiva de anexo, que no se expone: la lista de los 25 diagramas, cada uno con su código (A01 a A25, los que citan las notas) y un enlace que lo abre en el visor del sitio del proyecto, con zoom. Ante una pregunta, se hace clic en el diagrama; al terminar las preguntas se retrocede una diapositiva, al cierre con el código QR. Las preguntas probables y sus respuestas están en [defense-qa.md](defense-qa.md).

| Anexo | Diagrama (enlace con zoom) | Fuente | Diapositiva |
|---|---|---|---|
| A01 | [Arquitectura completa del piloto](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/complete-architecture) | `complete/architecture.svg` | 40 |
| A02 | [Trazabilidad de la IaC: cajas D01 a D13](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/complete-architecture-iac) | `complete/architecture-iac.svg` | 40 |
| A03 | [Zona de aterrizaje, gobierno y auditoría](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/accounts-landing-zone) | `accounts/landing-zone.svg` | 40 |
| A04 | [Piloto de 2020: qué se conserva, reemplaza y retira](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/legacy-2020) | `legacy/legacy-2020.svg` | 40 |
| A05 | [Plan de direccionamiento de la nube y de los sitios](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/network-addressing-plan) | `network/addressing-plan.svg` | 40 |
| A06 | [Conectividad de extremo a extremo](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/network-connectivity) | `network/connectivity.svg` | 40 |
| A07 | [Sin señal: búfer, reconexión y latencia de la alerta](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/network-no-signal-sequence) | `network/no-signal-sequence.svg` | 40 |
| A08 | [Patrón de red del centro de acopio](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/network-collection-center) | `network/collection-center.svg` | 40 |
| A09 | [Política de firewall perimetral y de nube](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/security-firewall-policy) | `security/firewall-policy.svg` | 40 |
| A10 | [Identidades, roles, puertas de entrada y llaves KMS](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/security-identity-and-access) | `security/identity-and-access.svg` | 40 |
| A11 | [Autenticación, MFA escalonado y revocación](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/security-revocation-sequence) | `security/revocation-sequence.svg` | 40 |
| A12 | [Monitoreo de finca y alerta al caficultor](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-farm-monitoring-sequence) | `flows/farm-monitoring-sequence.svg` | 40 |
| A13 | [Servicio de drones: de la alerta a la fumigación cerrada](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-drone-fumigation-sequence) | `flows/drone-fumigation-sequence.svg` | 40 |
| A14 | [Máquinas de estado del caso, la orden y la misión](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-drone-state-machines) | `flows/drone-state-machines.svg` | 40 |
| A15 | [Funciones de inferencia dirigidas por eventos](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-inference-functions) | `flows/inference-functions.svg` | 40 |
| A16 | [Saco, viaje y consulta del comprador](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-sack-and-trip-sequence) | `flows/sack-and-trip-sequence.svg` | 40 |
| A17 | [Estados del saco](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/flows-sack-states) | `flows/sack-states.svg` | 40 |
| A18 | [Camino de datos de la telemetría de finca](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/data-paths-telemetry) | `data-paths/telemetry.svg` | 40 |
| A19 | [Camino de datos de la posición del transportador](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/data-paths-transporter-position) | `data-paths/transporter-position.svg` | 40 |
| A20 | [Camino de datos de los objetos del dron](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/data-paths-drone-objects) | `data-paths/drone-objects.svg` | 40 |
| A21 | [Pipelines de ingesta y de objetos de vuelo](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/pipelines-ingestion-and-flight-objects) | `pipelines/ingestion-and-flight-objects.svg` | 40 |
| A22 | [Pipeline de la plataforma y modelo de versiones](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/pipelines-platform-pipeline) | `pipelines/platform-pipeline.svg` | 40 |
| A23 | [CI de la IaC: del pull request al plan](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/pipelines-iac-ci-sequence) | `pipelines/iac-ci-sequence.svg` | 40 |
| A24 | [CD de la IaC: subir la infraestructura con aprobación](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/pipelines-iac-provisioning-sequence) | `pipelines/iac-provisioning-sequence.svg` | 40 |
| A25 | [Bajar la infraestructura y volver atrás](https://aroma-pacifico.github.io/aroma-pacifico-web/#diagrama/pipelines-iac-teardown-and-rollback-sequence) | `pipelines/iac-teardown-and-rollback-sequence.svg` | 40 |
