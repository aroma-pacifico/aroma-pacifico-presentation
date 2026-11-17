# Guion de la sustentación

| Campo | Valor |
|---|---|
| Estado | Guion de ensayo. El tiempo de cada diapositiva es su texto leído a 130 palabras por minuto; el ensayo completo lo confirma. |
| Issue | aroma-pacifico/aroma-pacifico-roadmap#38 (A25) |
| Presentación | `deck/aroma-pacifico-sustentacion.pptx` y `.pdf`: 136 diapositivas, 1 a 63 de exposición y 64 a 135 de anexo, y la 136 repite el cierre con el código QR |
| Duración | 24:40 de exposición, dentro de la meta de 20 a 25 minutos |
| Fuente | Generado por `deck/build_deck.py` desde `deck/content.yaml`; las notas del orador del PPTX tienen el mismo texto. No se edita a mano. |

El guion está escrito para decirse en voz alta, en frases cortas, a unas 130 palabras por minuto. Cada presentador adapta la redacción; las cifras y las referencias son la parte fija. Toda cifra es del enunciado del caso, aritmética sobre una de ellas o una meta de diseño: se dice «meta de diseño» y nunca «medido». La fuente de cada diapositiva queda al final de su texto y en las notas del orador, no en la diapositiva.

En la portada, Esteban lee el título y pasa a la diapositiva del equipo, donde cada presentador dice su nombre y su rol en el orden de la exposición. Las diapositivas de diagrama completo duran poco: el presentador señala tres zonas y sigue; el detalle queda en el anexo para las preguntas.

## Reparto y tiempos

| Bloque | Presenta | Diapositivas | Tiempo |
|---|---|---|---|
| 1 | Esteban Gaviria Zambrano (SR1) | 1 a 15 | 6:55 |
| 2 | Karen Valeria Jurado Calpa (JR1) | 16 a 27 | 4:35 |
| 3 | Jeanpaul Atkinson Vidales Gallego (SR2) | 28 a 42 | 5:05 |
| 4 | César Augusto Jiménez Reina (JR2) | 43 a 55 | 4:45 |
| 5 | Esteban Gaviria Zambrano (SR1) | 56 a 63 | 3:20 |
| Total | SR1 10:15, JR1 4:35, SR2 5:05, JR2 4:45 | 1 a 63 | 24:40 |

## Guion por diapositiva

### Bloque 1: Esteban Gaviria Zambrano (SR1), diapositivas 1 a 15, 6:55

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

No copiamos la arquitectura de 2020, como pide el caso. De 18 elementos, conservamos 8 requisitos que siguen vigentes, reemplazamos 4 supuestos de conectividad que ya no se cumplen y retiramos 6 elementos, como los precios y el manual de 2020. El diagrama siguiente muestra la trazabilidad de cada uno.

Fuente: Arquitectura, sección 13 · legacy-2020.md · legacy/legacy-2020.svg.

**Diapositiva 7 (0:15). Cada elemento de 2020 tiene un destino trazable en el diseño 2026**

A la izquierda lo que traía 2020, a la derecha su destino en 2026 y la caja de IaC que lo implementa. El detalle completo está en el anexo.

Fuente: aroma-pacifico-diagrams, legacy/legacy-2020.svg.

**Diapositiva 8 (0:40). Dimensionamos con las cifras del caso, de hoy y a cinco años**

Dimensionamos con las cifras del caso. Al día entran 1.200 lecturas de cultivo y, en cosecha, 2.400 de secado; 7.200 posiciones de transportadores y hasta 1.200 sacos. La consulta del saco tiene picos de 30 por minuto, y en un mes de cosecha hay 108.270 invocaciones de funciones y solo 420 llamadas al modelo.
A cinco años son 13 millones de posiciones y 2,19 millones de sacos. Y a 1.000 fincas la ingesta sube a 18.000 lecturas diarias, 0,21 por segundo: el patrón no cambia.

Fuente: Monitoreo de finca, sección 3 · Saco y viaje, sección 8 · Plan de direccionamiento, sección 6 · Costos del piloto, sección 6.4.

**Diapositiva 9 (0:45). Elegimos AWS en us-east-1 y dejamos Azure preparada sin duplicar la plataforma**

La nube principal es AWS, en una sola región, us-east-1. Los criterios: que funciones, almacenamiento e inferencia administrada vivan en la misma región, para decir a qué país y a qué región salen los objetos; que las 28 reglas IaC del equipo ya estén escritas para AWS; y no duplicar la plataforma.
sa-east-1 no permite nombrar la región de la inferencia de visión, y Azure o GCP como principal exigiría reescribir las reglas dentro de las 100 horas. Azure queda preparada con tres propiedades: interfaces neutrales, datos en formato abierto y un destino de exportación declarado, sin desplegar nada.

Fuente: ADR-001, contexto, decisión y alternativas.

**Diapositiva 10 (0:20). Una plataforma por eventos en una región, con el borde diseñado para operar sin señal**

La arquitectura objetivo cabe en cuatro ideas. Una organización con cinco cuentas y un /16 por ambiente. Un borde autónomo que guarda y libera al confirmar. Cómputo solo por eventos, sin servidores esperando. Y datos cifrados con llaves propias por almacén, guardados cinco años. Veamos el diagrama completo.

Fuente: Arquitectura, secciones 1, 4, 5 y 7 · complete/architecture.svg.

**Diapositiva 11 (0:30). La arquitectura completa: borde, organización AWS y cajas D01 a D13**

Arriba, el borde: fincas, centros de acopio, la operación contratada de drones y el transporte con la consulta pública. Abajo, la organización AWS, con la IaC a la izquierda y la cuenta de producción a la derecha. Las insignias D01 a D13 marcan lo que construye el código. Al pie, los dos flujos de negocio: la custodia del saco y de la plaga a la fumigación.

Fuente: aroma-pacifico-diagrams, complete/architecture.svg.

**Diapositiva 12 (0:15). En el borde, cada actor guarda localmente y publica al recuperar la señal**

En el detalle del borde se ve la regla común: el nodo de finca, la estación de tierra y el teléfono del transportador guardan cifrado y liberan solo al confirmar la recepción.

Fuente: aroma-pacifico-diagrams, complete/architecture.svg (detalle).

**Diapositiva 13 (0:15). En producción, la VPC no tiene salida a internet y todo corre por eventos**

En la cuenta de producción, los niveles son privados y llegan a AWS por endpoints. Las funciones se disparan por eventos y escriben en DynamoDB y S3 cifrados con llaves propias.

Fuente: aroma-pacifico-diagrams, complete/architecture.svg (detalle).

**Diapositiva 14 (0:40). Gobernamos desde la raíz: políticas, etiquetas, presupuestos y auditoría**

El gobierno se aplica desde la raíz: siete políticas de control de servicios, entre ellas solo us-east-1, sin credenciales de larga duración y cambios de producción solo por el pipeline. La política de etiquetas fija ocho claves y cinco reparten el costo por fincas, drones, acopio, viajes y ambientes.
Los presupuestos son de 650 dólares en mes normal y 700 en cosecha, con alertas al 80 y al 100 por ciento, y el trail de la organización guarda cinco años los cuatro eventos que el caso pide auditar.

Fuente: Zona de aterrizaje, secciones 3 a 7 · accounts/landing-zone.svg.

**Diapositiva 15 (0:15). La zona de aterrizaje separa cuentas y aplica controles desde la raíz**

Arriba la raíz y las cuentas; en el medio las cuatro puertas de identidad, el camino de presupuestos y el canal de auditoría; abajo la tabla de etiquetas. Con esto Karen continúa con la red.

Fuente: aroma-pacifico-diagrams, accounts/landing-zone.svg.

*Transición: Esteban cede la palabra a Karen, que continúa en la diapositiva 16.*

### Bloque 2: Karen Valeria Jurado Calpa (JR1), diapositivas 16 a 27, 4:35

**Diapositiva 16 (0:35). Identidad, no dirección: la red crece de 200 a 1.000 fincas sin redireccionar**

La regla de la red es identidad, no dirección. Fincas, teléfonos y drones no tienen dirección en la nube; se autentican con un certificado o un token. Por eso crecer de 200 a 1.000 fincas suma identidades, no subredes.
Cada ambiente tiene su /16: 10.80 desarrollo, 10.81 pruebas y 10.82 producción, sin tocar el 10.40 barra 13 de los centros. Hay reservas para AWS y un bloque para Azure, que no se despliega.

Fuente: Plan de direccionamiento, secciones 2 a 6 · network/addressing-plan.svg.

**Diapositiva 17 (0:15). Cada ambiente tiene su VPC y los mismos siete roles de subred**

La VPC repite los mismos niveles en tres zonas de disponibilidad, con /22 por zona y reserva para crecer. A la derecha, el patrón de los tres centros.

Fuente: aroma-pacifico-diagrams, network/addressing-plan.svg.

**Diapositiva 18 (0:30). Siete flujos de conectividad, cada uno con protocolo, búfer y conducta sin señal**

Este es el diseño de conectividad, en el cuerpo de la propuesta y no en un anexo. La finca publica MQTT sobre TLS con certificado X.509; la finca sin cobertura usa el mismo nodo con portador satelital; el dron baja sus objetos por el centro o por la cabecera municipal; el transportador publica cada 5 minutos con bandeja cifrada; y el puerto solo registra la entrega.

Fuente: aroma-pacifico-diagrams, network/connectivity.svg · Conectividad, secciones 2 a 11.

**Diapositiva 19 (0:35). Sin señal no se pierde nada: cada actor guarda y libera al confirmar**

Sin señal no se pierde nada. El nodo guarda hasta 24 horas cifradas; al volver publica primero una lectura en vivo y luego vacía el búfer. La finca sin cobertura usa el mismo nodo por satélite. La app del transportador guarda 7 días y nunca descarta un evento de custodia. Y la misión del dron viaja precargada.
En la nube, cada lectura se deduplica por nodo y hora, así que un reintento no duplica alertas.

Fuente: Conectividad, secciones 4.3, 6, 7 y 8 · ASM-073 a ASM-079 · network/no-signal-sequence.svg.

**Diapositiva 20 (0:20). La alerta cabe en 300 segundos: 210 de presupuesto y 90 de margen**

A la izquierda, la pérdida de señal, el búfer y la reconexión con drenado ordenado. A la derecha, el presupuesto de latencia en siete saltos: 210 segundos de meta y 90 de margen dentro de los 300 del caso.

Fuente: aroma-pacifico-diagrams, network/no-signal-sequence.svg.

**Diapositiva 21 (0:35). Un solo patrón de LAN sirve a los tres centros; en el puerto no instalamos nada**

En los centros de acopio, un solo patrón sirve a los tres departamentos con dos parámetros: la clave del centro y el segundo octeto. Siete zonas con su SSID; la de visitantes no llega a logística ni a gerencia.
La WAN es de 100 megabits con dos túneles IPsec y respaldo celular; el pico pide 68 y planeamos 90. En Buenaventura no instalamos nada: la naviera conserva su telemetría y nosotros registramos la entrega desde la app del transportador.

Fuente: Red del centro de acopio, secciones 2 a 6 · Conectividad, sección 10 · network/collection-center.svg.

**Diapositiva 22 (0:10). El centro de acopio: zonas segmentadas detrás de un firewall perimetral**

Cada flecha verde es una regla permitida con su ID y puerto, y cada roja una denegación. Este patrón se repite tres veces sin redibujar.

Fuente: aroma-pacifico-diagrams, network/collection-center.svg.

**Diapositiva 23 (0:25). Firewall en cada centro y en la nube, sin NAT gateway ni appliance de red**

Hay un firewall perimetral en cada centro y uno de nube, con tablas de origen, destino, puerto, acción y vigencia. No compramos NAT gateway ni appliance: llegamos a AWS por endpoints privados, la capa de datos no tiene ruta a internet y eso ahorra 10.856 dólares netos al año.

Fuente: Política de firewall, secciones 3 a 6 · Costos del piloto, sección 9 · security/firewall-policy.svg.

**Diapositiva 24 (0:10). Las reglas del centro y de la nube, nivel por nivel**

A la izquierda el firewall del centro, en el medio el hub de tránsito y a la derecha cada nivel de la VPC con sus reglas.

Fuente: aroma-pacifico-diagrams, security/firewall-policy.svg.

**Diapositiva 25 (0:35). Identidades separadas, MFA donde hay riesgo y revocación inmediata**

Cada rol del caso tiene su identidad con mínimo privilegio, y el MFA es obligatorio para el operario de acopio, el operador de drones, el de plataforma y el agrónomo, que además se reautentica para autorizar una fumigación.
Ocho llaves KMS con rotación cifran cada clase de datos. Un nodo o un dron perdido pierde su certificado y su conexión; la meta es completar la baja en 4 horas desde el reporte. El comprador solo ve cuatro grupos de datos.

Fuente: Seguridad e identidad, secciones 2 a 10 · ASM-098 · security/identity-and-access.svg · security/revocation-sequence.svg.

**Diapositiva 26 (0:10). Cada actor entra por su puerta, con su directorio y su llave**

De izquierda a derecha: el tipo de identidad, su directorio, la puerta de entrada, el rol que procesa y el almacén con su llave.

Fuente: aroma-pacifico-diagrams, security/identity-and-access.svg.

**Diapositiva 27 (0:15). MFA escalonado para autorizar y revocación con tiempos definidos**

Arriba, el ingreso con MFA y la reautenticación para autorizar, y la consulta anónima del comprador. Abajo, la revocación de un nodo o dron y la salida de una persona. Jeanpaul sigue con las cargas.

Fuente: aroma-pacifico-diagrams, security/revocation-sequence.svg.

*Transición: Karen cede la palabra a Jeanpaul, que continúa en la diapositiva 28.*

### Bloque 3: Jeanpaul Atkinson Vidales Gallego (SR2), diapositivas 28 a 42, 5:05

**Diapositiva 28 (0:30). Del sensor al teléfono del caficultor en siete saltos y menos de 5 minutos**

El monitoreo de finca recorre siete saltos, cada uno con su meta: suman 210 segundos y dejan 90 de margen dentro de los 300 del caso. La función evalúa contra los umbrales que publica la Federación, que son datos y no código.
Abrimos una alerta por episodio, no por lectura, y la entregamos por SMS y push. El historial queda cinco años.

Fuente: Monitoreo de finca, secciones 3 a 7 · Conectividad, sección 8 · flows/farm-monitoring-sequence.svg.

**Diapositiva 29 (0:10). Monitoreo de finca: cada salto tiene meta y cada lectura deja rastro**

La secuencia muestra los siete saltos con su meta, la deduplicación del episodio y la entrega por dos canales.

Fuente: aroma-pacifico-diagrams, flows/farm-monitoring-sequence.svg.

**Diapositiva 30 (0:35). El modo combinado es el único que cubre los cinco servicios del dron**

El caso pide cinco servicios y ninguno reemplaza a otro. El modo área delimita el lote y estima la cosecha; el modo precisión confirma la alerta, fumiga el foco y verifica el mismo lote. Solo el combinado cubre los cinco.
El cambio de modo son dos eventos persistidos y solo un foco confirmado lleva a una orden. Vuela un operador certificado contratado y autoriza un agrónomo con MFA: es el ADR-002.

Fuente: ADR-002, modo de vuelo y gobierno del dron · Servicio de drones, secciones 3 a 6.

**Diapositiva 31 (0:10). De la alerta a la fumigación cerrada, en cinco fases persistidas**

La secuencia completa tiene cinco fases. Ningún paso cambia de estado sin persistir su evidencia.

Fuente: aroma-pacifico-diagrams, flows/drone-fumigation-sequence.svg.

**Diapositiva 32 (0:15). La orden de fumigación solo sale con autorización humana y MFA**

En el detalle, la fase de autorización: el caso confirmado crea un borrador, el agrónomo lo revisa y lo autoriza con MFA, y la plataforma guarda quién autorizó, la ventana y el operador.

Fuente: aroma-pacifico-diagrams, flows/drone-fumigation-sequence.svg (detalle).

**Diapositiva 33 (0:15). Tres máquinas de estado impiden fumigar sin evidencia**

El caso, la orden y la misión son máquinas de estado. La orden no sale sin polígono ni registro de vuelo cerrado, y la fumigación no se cierra hasta persistir la verificación.

Fuente: aroma-pacifico-diagrams, flows/drone-state-machines.svg.

**Diapositiva 34 (0:30). Un orquestador por eventos coordina las capacidades del dron sin acoplarlas**

Un orquestador dirigido por eventos coordina las capacidades del dron sin acoplarlas: el objeto persistido dispara un pipe de EventBridge, una regla por tipo de misión lo envía a su cola y cada cola tiene su cola de fallidos. Es el ADR-004.
Si una invocación falla, el objeto se queda y el caso no cambia; el error se observa en la cola de fallidos.

Fuente: ADR-004 · Funciones de inferencia, secciones 3, 4 y 6.

**Diapositiva 35 (0:30). Cuatro funciones, una por disparador, y el modelo solo cuando abre una alerta**

La inferencia es por eventos: cuatro funciones, una por disparador. Cada una lee el objeto ya persistido, llama a Amazon Nova Pro en us-east-1 y escribe en el expediente con hora, confianza y origen.
En un mes de cosecha son 108.270 invocaciones, pero solo 420 llegan al modelo, porque solo se llama al abrir una alerta: 5,21 dólares. Una foto con una persona no se envía.

Fuente: Funciones de inferencia, secciones 2 a 10 · Costos del piloto, sección 6 · flows/inference-functions.svg.

**Diapositiva 36 (0:10). Disparadores, colas, funciones y almacenes de la inferencia**

De izquierda a derecha: disparadores, colas con su cola de fallidos, las cuatro funciones, la inferencia y los almacenes, y la observación de errores.

Fuente: aroma-pacifico-diagrams, flows/inference-functions.svg.

**Diapositiva 37 (0:30). El saco se rastrea en siete estados y el comprador solo ve lo que le corresponde**

El saco pasa por siete estados, de en preparación a entregado en puerto, aceptado o rechazado. Cada evento guarda fecha, hora y responsable en un registro de solo agregar, con RPO de 15 minutos.
El código es aleatorio y no revela la cédula. La consulta pública lee una vista separada, con RTO de 4 horas, y el comprador ve solo origen, fechas, estado y secado.

Fuente: Saco y viaje, secciones 2 a 8 · flows/sack-and-trip-sequence.svg · flows/sack-states.svg.

**Diapositiva 38 (0:10). Del código impreso a la consulta del comprador, en seis fases**

La secuencia sigue al saco desde la hoja de códigos hasta la consulta pública, con la bandeja cifrada del transportador en ruta.

Fuente: aroma-pacifico-diagrams, flows/sack-and-trip-sequence.svg.

**Diapositiva 39 (0:10). Los siete estados del saco y quién responde por cada transición**

Cada transición tiene responsable y evento; el acopio y el puerto pueden aceptar o rechazar.

Fuente: aroma-pacifico-diagrams, flows/sack-states.svg.

**Diapositiva 40 (0:30). Tres caminos de datos distintos, cada uno con su almacén correcto**

Los tres caminos de datos que pide el caso son distintos a propósito. La telemetría entra por MQTT a IoT Core y termina en DynamoDB. La posición entra por HTTPS a la API. Los objetos del dron suben a S3 por la VPN del centro o con una URL firmada desde la cabecera municipal. Los eventos del saco y las órdenes van a la base transaccional.

Fuente: Conectividad, secciones 4, 6 y 7 · data-paths/data-paths.md · Automatización y pipelines, secciones 6 y 7.

**Diapositiva 41 (0:10). Los pipelines de ingesta y de objetos de vuelo, de punta a punta**

Estos son los dos pipelines que pide el caso además del de plataforma: ingesta y recepción de objetos de vuelo.

Fuente: aroma-pacifico-diagrams, pipelines/ingestion-and-flight-objects.svg.

**Diapositiva 42 (0:30). Dos SLO medibles y las cinco detecciones del caso, en dos tableros**

Observamos lo que el caso pide: ingesta, aplicaciones, bases, los tres enlaces WAN y la llegada de objetos de vuelo. Dos SLO con su SLI: la entrega de la alerta y la disponibilidad de la consulta del saco.
Las cinco detecciones del caso tienen su alarma, y hay dos tableros, operativo y de costos, partidos por etiquetas. César sigue con la infraestructura como código.

Fuente: Observabilidad, secciones 2 a 6 · docs/dashboards.

*Transición: Jeanpaul cede la palabra a César, que continúa en la diapositiva 43.*

### Bloque 4: César Augusto Jiménez Reina (JR2), diapositivas 43 a 55, 4:45

**Diapositiva 43 (0:30). La IaC cabe en 100 horas porque construye un ambiente patrón y nada más**

La infraestructura como código cabe en 100 horas porque construye lo que el caso cuenta: módulos, variables, estado remoto y un plan ejecutable de un ambiente patrón. Elegimos Terraform porque nuestras 28 reglas están escritas para él. El estado vive en un bucket cifrado y versionado por ambiente, con bloqueo nativo. Lo que queda fuera es deliberado y está escrito en el ADR-003.

Fuente: ADR-003 · Plan de 100 horas, sección 2.

**Diapositiva 44 (0:10). Trece cajas, trece tareas: el código coincide con el diagrama**

Cada caja es una tarea del plan y una ruta del repositorio. D11, D13 y D12 forman la cadena del plan revisable.

Fuente: aroma-pacifico-diagrams, complete/architecture-iac.svg.

**Diapositiva 45 (0:30). Ocho módulos públicos, versionados por etiqueta, uno por caja**

Este es el catálogo del repositorio público de módulos: ocho módulos, cada uno con su caja y la etiqueta en que se publicó, de la v0.1.0 a la v0.5.0. Ninguno declara proveedor, backend ni cuentas, porque el repositorio es público, y tienen 131 pruebas en modo plan en 8 suites. Los stacks los consumen por etiqueta, así que subir de versión es un cambio revisado.

Fuente: aroma-pacifico-terraform-modules: etiquetas v0.1.0 a v0.5.0, README y tests de cada módulo · pc-iac-015.

**Diapositiva 46 (0:35). Cuatro stacks en orden de dependencia y tres ambientes con la misma receta**

La infraestructura tiene cuatro stacks, uno por dominio, en orden de dependencia: estado, red, seguridad y cargas. Los tres ambientes, dev, qa y pdn, usan los mismos módulos y las mismas etiquetas; cambian solo su archivo de variables, su backend y su CIDR.
El plan de extremo a extremo de qa corre contra el emulador Floci, los cuatro stacks en orden, y valida que no haya secretos en la historia ni en el plan.

Fuente: aroma-pacifico-infrastructure: stacks/, environments/, scripts/plan-all.sh, docs/b13-final-validation.md · ADR-003.

**Diapositiva 47 (0:20). Veintiocho reglas vinculantes gobiernan cada línea de Terraform**

Las 28 reglas pc-iac son vinculantes y la CI comprueba las que se pueden verificar. Cubren la estructura del módulo, variables y locals, proveedores y versiones, estado y dominios, seguridad, recursos, pruebas, y desde este mes el costo con Infracost y el plan contra Floci.

Fuente: standards/iac-rules, pc-iac-001 a pc-iac-028 · AGENTS.md, sección 8.

**Diapositiva 48 (0:25). Cada pull request pasa trece chequeos y llega a un plan con su costo**

Así entra un cambio. El pull request pasa el escaneo de secretos, las compuertas de cada stack, el plan contra Floci e Infracost, que publica el costo antes, después y la diferencia junto al plan. Son 13 chequeos por pull request de infraestructura y 29 en el de módulos. Al fusionar, un módulo nuevo se publica por etiqueta.

Fuente: aroma-pacifico-infrastructure: infrastructure-ci.yml, floci-plan.yml, infracost.yml, pr-conventions.yml · pc-iac-027 · pc-iac-028.

**Diapositiva 49 (0:10). CI de la IaC: del pull request al plan revisado y la etiqueta**

La secuencia muestra los mismos pasos con sus actores.

Fuente: aroma-pacifico-diagrams, pipelines/iac-ci-sequence.svg.

**Diapositiva 50 (0:30). Subir la infraestructura: producción aplica solo el plan revisado y aprobado**

Subir la infraestructura sigue la promoción dev, qa y pdn. Cada merge planifica dev y qa con su costo. Para producción, una primera ejecución publica el plan, el delta de costo y la huella del plan; otra persona de la lista de aprobadores aprueba exactamente esa huella. El pipeline rechaza la ventana de cosecha salvo un incidente, y solo se aplica el plan aprobado. Todo queda registrado.

Fuente: aroma-pacifico-infrastructure: cd-promotion.yml, cd-plan.yml, docs/cd-pipeline.md, secciones 2 a 5.

**Diapositiva 51 (0:10). Subir la infraestructura, stack por stack y con aprobación**

La secuencia muestra la promoción con sus actores y la aprobación con evidencia.

Fuente: aroma-pacifico-diagrams, pipelines/iac-provisioning-sequence.svg.

**Diapositiva 52 (0:25). Bajar y volver atrás también pasa por un plan revisado**

Volver atrás es un revert por pull request y una nueva promoción: el plan revisado muestra el cambio inverso. Bajar un ambiente va en el orden inverso de los stacks, y el aprobador lee primero las destrucciones. Las tablas con datos tienen prevent_destroy, así que un plan que las reemplace falla, y el estado se recupera del bucket versionado.

Fuente: aroma-pacifico-infrastructure, docs/cd-pipeline.md, secciones 3 y 7 · Automatización y pipelines, secciones 5 y 10.

**Diapositiva 53 (0:10). Bajar la infraestructura y volver atrás, con la misma compuerta**

La secuencia muestra el revert, la baja controlada y las guardas de retención.

Fuente: aroma-pacifico-diagrams, pipelines/iac-teardown-and-rollback-sequence.svg.

**Diapositiva 54 (0:20). 98 horas en 19 partes, repartidas por rol y por semana**

El plan reparte 98 horas en 19 partes. SR1 lleva 27, SR2 26, JR1 22 y JR2 23. Seis tareas se dividen en módulo y cableado, ninguna pasa de 10 horas y nadie pasa de 25 por semana ni de 5 por día. Quedan 2 horas de reserva.

Fuente: Plan de 100 horas, secciones 4.1 y 6.5.

**Diapositiva 55 (0:30). La ruta crítica dura 38 horas y termina el día 8 de 10**

La ruta crítica tiene dos cadenas de 38 horas que comparten B01, B06a, B03 y B04b; una sigue por B09b, B07b y B12, y la otra por B08 y B05, y ambas cierran en B13. El plan termina en la hora 38 de 50, el día 8, con 12 horas de colchón, y usa el 49 por ciento de la capacidad. Esteban cierra con los costos.

Fuente: Plan de 100 horas, secciones 6.2, 6.4 y 6.5.

*Transición: César cede la palabra a Esteban, que continúa en la diapositiva 56.*

### Bloque 5: Esteban Gaviria Zambrano (SR1), diapositivas 56 a 63, 3:20

**Diapositiva 56 (0:30). El piloto cuesta USD 2.707 en un mes normal y USD 10.639 en cosecha**

El piloto cuesta 2.707 dólares en un mes normal y 10.639 en un mes de cosecha, con 82.550 de inversión inicial. La nube es la parte menor: 559 y 574 dólares, bajo los topes de 650 y 700. Cada finca cuesta 370 dólares de hardware una vez y 4,60 al mes, y la inferencia de un mes de cosecha, 5,21.

Fuente: Costos del piloto, secciones 1, 3, 5, 6 y 7 · ASM-230, ASM-231, ASM-250.

**Diapositiva 57 (0:25). La cosecha la encarece el dron, no la nube: AWS sube solo USD 14,81**

A la izquierda, el costo por dominio: lo que dispara la cosecha es la campaña de dron, que pasa de 583 a 8.500 dólares. A la derecha, la nube por servicio: pesa la red privada, con el resolver, el Transit Gateway y las VPN. La cosecha solo sube la nube 14,81 dólares, por los SMS y la inferencia.

Fuente: Costos del piloto, secciones 1, 3.2 y 7.1 · ASM-230 a ASM-237.

**Diapositiva 58 (0:35). Seis decisiones ahorran USD 47.533 al año y evitan USD 230.000 de inversión**

Seis decisiones bajan el costo: endpoints en vez de Network Firewall y NAT, CloudFront en vez de un balanceador, el modelo solo al abrir una alerta, hardware dual con satélite solo sin señal, drones contratados y DynamoDB bajo demanda. Suman 47.533 dólares al año y 230.000 de inversión evitada.
Y el costo no se descuida después: Infracost publica el costo antes, después y la diferencia en cada pull request y en la aprobación de producción.

Fuente: Costos del piloto, secciones 1, 2 y 9 · ASM-251 · pc-iac-027.

**Diapositiva 59 (0:30). Cada cambio se aprueba, se avisa y se puede volver atrás**

El cambio es controlado: un mismo candidato pasa por dev, qa y pdn, y producción aplica solo lo revisado, nunca en el día de una semana de cosecha salvo un incidente. Las dos plantillas de notas de versión dicen qué cambia, la ventana, el impacto, la aprobación, el aviso a la Federación y cómo volver atrás, cada una con su ejemplo.

Fuente: Automatización y pipelines, secciones 3 a 5 y 10 · Notas de versión · pipelines/platform-pipeline.svg.

**Diapositiva 60 (0:10). Un candidato, tres ambientes y salvaguardas en producción**

El pipeline de la plataforma: un candidato inmutable que se promueve con compuertas, despliegue canario de funciones y alarmas de vuelta atrás.

Fuente: aroma-pacifico-diagrams, pipelines/platform-pipeline.svg.

**Diapositiva 61 (0:30). Un sistema de diseño propio para las tres apps, legible a pleno sol**

El sistema de diseño es propio, como pide el caso: marca, paleta con los estados del saco y la alerta, tipografía para teléfono y web, y componentes base. El contraste es de 7 a 1 en los 48 pares de color, las áreas táctiles son de 48 y 56 píxeles y la consulta pública no muestra datos personales. Esta misma presentación usa sus tokens.

Fuente: aroma-pacifico-design-system: tokens/contrast-report.md, docs/design-system.md, previews/.

**Diapositiva 62 (0:20). Por qué esta propuesta**

Por qué esta propuesta: funciona sin señal, gobierna los drones con autorización humana, entrega código que coincide con el diagrama dentro de las 100 horas y mantiene el costo bajo control desde el diseño hasta cada pull request.

Fuente: Síntesis de la propuesta.

**Diapositiva 63 (0:20). Gracias**

Gracias. El código QR lleva al sitio de Aroma Pacífico, con la arquitectura, cada diagrama en alta resolución, la IaC, los costos y el sistema de diseño. Recibimos sus preguntas; el anexo tiene cada diagrama completo y sus detalles.

## Anexo para preguntas

Después del cierre y el código QR viene el anexo, que no se expone. Tiene cada diagrama publicado en vista completa, sin recortes, y sus vistas de detalle donde el texto del diagrama quedaría por debajo de unos 10 px a 1920 de ancho. Cada diagrama, completo o en detalle, enlaza a su vista en alta resolución en el sitio del proyecto. Ante una pregunta, quien responde salta a la diapositiva de la tabla; al terminar las preguntas se pasa a la última diapositiva, que repite el cierre con el código QR. Las preguntas probables y sus respuestas están en [defense-qa.md](defense-qa.md).

| Anexo | Diagrama | Fuente | Diapositivas |
|---|---|---|---|
| A01 | Arquitectura completa del piloto | `complete/architecture.svg` | 64 a 70 |
| A02 | Trazabilidad de la IaC: cajas D01 a D13 | `complete/architecture-iac.svg` | 71 |
| A03 | Zona de aterrizaje, gobierno y auditoría | `accounts/landing-zone.svg` | 72 a 75 |
| A04 | Piloto de 2020: qué se conserva, reemplaza y retira | `legacy/legacy-2020.svg` | 76 a 79 |
| A05 | Plan de direccionamiento de la nube y de los sitios | `network/addressing-plan.svg` | 80 a 82 |
| A06 | Conectividad de extremo a extremo | `network/connectivity.svg` | 83 a 85 |
| A07 | Sin señal: búfer, reconexión y latencia de la alerta | `network/no-signal-sequence.svg` | 86 a 88 |
| A08 | Patrón de red del centro de acopio | `network/collection-center.svg` | 89 a 91 |
| A09 | Política de firewall perimetral y de nube | `security/firewall-policy.svg` | 92 a 94 |
| A10 | Identidades, roles, puertas de entrada y llaves KMS | `security/identity-and-access.svg` | 95 a 97 |
| A11 | Autenticación, MFA escalonado y revocación | `security/revocation-sequence.svg` | 98 a 100 |
| A12 | Monitoreo de finca y alerta al caficultor | `flows/farm-monitoring-sequence.svg` | 101 a 103 |
| A13 | Servicio de drones: de la alerta a la fumigación cerrada | `flows/drone-fumigation-sequence.svg` | 104 a 106 |
| A14 | Máquinas de estado del caso, la orden y la misión | `flows/drone-state-machines.svg` | 107 a 110 |
| A15 | Funciones de inferencia dirigidas por eventos | `flows/inference-functions.svg` | 111 a 113 |
| A16 | Saco, viaje y consulta del comprador | `flows/sack-and-trip-sequence.svg` | 114 a 116 |
| A17 | Estados del saco | `flows/sack-states.svg` | 117 a 119 |
| A18 | Camino de datos de la telemetría de finca | `data-paths/telemetry.svg` | 120 |
| A19 | Camino de datos de la posición del transportador | `data-paths/transporter-position.svg` | 121 |
| A20 | Camino de datos de los objetos del dron | `data-paths/drone-objects.svg` | 122 a 124 |
| A21 | Pipelines de ingesta y de objetos de vuelo | `pipelines/ingestion-and-flight-objects.svg` | 125 a 129 |
| A22 | Pipeline de la plataforma y modelo de versiones | `pipelines/platform-pipeline.svg` | 130 a 132 |
| A23 | CI de la IaC: del pull request al plan | `pipelines/iac-ci-sequence.svg` | 133 |
| A24 | CD de la IaC: subir la infraestructura con aprobación | `pipelines/iac-provisioning-sequence.svg` | 134 |
| A25 | Bajar la infraestructura y volver atrás | `pipelines/iac-teardown-and-rollback-sequence.svg` | 135 |
