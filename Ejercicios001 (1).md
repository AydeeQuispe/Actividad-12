**Pregunta 1:** Implementa un sistema basado en eventos en Python que simule cómo los Jupyter Notebooks manejan eventos e interacciones de usuario. Esto incluye crear un bucle de eventos, manejar diferentes tipos de eventos y actualizar el estado de un notebook simulado basado en interacciones de usuario.

El código debe incluir:

- Usar asyncio para manejar la ejecución asíncrona de celdas y el manejo de eventos.
- Implementar mecanismos de manejo de errores y registro de logs para diferentes tipos de errores.
- Asegurae operaciones seguras en los hilos al acceder a recursos compartidos.
- Implementa un sistema para filtrar y priorizar eventos según su importancia o tipo.

**Pregunta 2:** Crea un sistema de coordinación de tareas en una red de robots industriales:

- Usa el algoritmo de Chandy-Lamport para tomar instantáneas del estado global de los robots durante la ejecución de n tareas.
- Implementa el algoritmo de Raymond para la exclusión mutua en el acceso a recursos compartidos entre los robots.
- Utiliza relojes vectoriales para asegurar el ordenamiento parcial de los eventos y detectar violaciones de causalidad.
- Integra un recolector de basura generacional para la gestión eficiente de la memoria en los nodos de control de los robots.

**Pregunta 3:** Implementa un sistema distribuido en Python para la ejecución de tareas científicas en una red de computadoras, utilizando los siguientes algoritmos:

1. **Dijkstra-Scholten** para la detección de terminación de procesos distribuidos.
1. **Ricart-Agrawala** para la exclusión mutua en el acceso a recursos compartidos.
1. **Sincronización de relojes** para asegurar que todos los nodos tengan una vista consistente del tiempo.
1. **Algoritmo de recolección de basura (Cheney)** para gestionar la memoria en los nodos de computación.

**Instrucciones**

**Crear una clase Message:**

- Esta clase debe tener atributos para el remitente (sender), el contenido (content) y la marca de tiempo (timestamp).

**Crea una clase Node:**

- Cada nodo debe tener un identificador (node\_id), el número total de nodos en la red (total\_nodes), y una referencia a la red.
- Implementa métodos para enviar mensajes a otros nodos, manejar solicitudes de exclusión mutua utilizando el algoritmo de Ricart-Agrawala, y detectar la terminación de procesos distribuidos con el algoritmo de Dijkstra-Scholten.
- Implementa un método para sincronizar los relojes de los nodos.
- Implementa un método para realizar la recolección de basura utilizando el algoritmo de Cheney.

**Crea una clase Network:**

- Esta clase debe manejar la creación y la coordinación de los nodos en la red.
- Implementar métodos para iniciar y detener la red de nodos.

**Simula la ejecución de tareas científicas:**

- Sincroniza los relojes de los nodos.
- Realiza solicitudes de exclusión mutua para acceder a recursos compartidos.
- Realiza la recolección de basura en los nodos.
- Detiene la red de nodos de manera ordenada.

**Pregunta 4 :** Implementar un sistema distribuido en Python que simule las tres propiedades del Teorema CAP: consistencia, disponibilidad y tolerancia a particiones. El sistema debe demostrar cómo se comporta bajo diferentes configuraciones.

En el código debes incluir:

- La simulación de latencia de red en la comunicación entre nodos.
- Un algoritmo de consenso sencillo como Raft o Paxos para gestionar la consistencia.
- Fallos aleatorios en los nodos para simular fallos de red o nodos caídos.
- Registros de operaciones y versiones de datos para gestionar la consistencia eventual.
- Diferentes configuraciones de particiones y curaciones en la red.
- Primero se realiza las importaciones![](Aspose.Words.99abc9e3-1440-4111-b872-d984b22e75fe.001.png)

import asyncio # Importa el módulo asyncio para soportar programación asíncrona.

import logging # Importa el módulo logging para registrar eventos y mensajes.

import queue # Importa el módulo queue para usar PriorityQueue, una cola de prioridad.

import threading # Importa el módulo threading para manejar bloqueos y concurrencia.

from concurrent.futures import ThreadPoolExecutor # Importa ThreadPoolExecutor para ejecutar tareas en hilos.

from enum import Enum # Importa Enum para definir tipos de eventos como enumeraciones.

- En este caso se importa nest\_asyncio si estás en un entorno de notebook

  import nest\_asyncio # Importa nest\_asyncio para anular la política asyncio en entornos de notebooks.

  nest\_asyncio.apply() # Aplica la anulación de asyncio para entornos de notebooks.

- Se realiza la Configuración de logging logging.basicConfig(level=logging.INFO) # Configura el nivel de logging a INFO.

  logger = logging.getLogger(\_\_name\_\_) # Crea un logger con el nombre del módulo actual.![ref1]

- Definicion de tipos de eventos como una enumeración

class EventType(Enum):

CELL\_EXECUTION = 1 # Tipo de evento para la ejecución de una celda.

USER\_INPUT = 2 # Tipo de evento para la entrada de usuario.

SYSTEM\_UPDATE = 3 # Tipo de evento para la actualización del sistema.

ERROR = 4 # Tipo de evento para manejar errores.

- Definicion de Clase para representar un evento con tipo, datos y prioridad

  class Event:

def \_\_init\_\_(self, event\_type, data=None, priority=1): self.event\_type = event\_type # Tipo de evento (enum). self.data = data # Datos asociados al evento (opcional).

self.priority = priority # Prioridad del evento en la cola (menor es más prioritario).

def \_\_lt\_\_(self, other):

return self.priority < other.priority # Comparación de prioridad para la cola de prioridad.

- Sistema basado en eventos

class EventSystem:

def \_\_init\_\_(self):

self.event\_queue = queue.PriorityQueue() # Inicializa una cola de prioridad vacía.

self.executor = ThreadPoolExecutor() # Inicializa un executor de hilos para tareas concurrentes.

self.lock = threading.Lock() # Inicializa un objeto de bloqueo para sincronización.

def add\_event(self, event):

with self.lock: # Adquiere el bloqueo antes de operar sobre la cola de eventos.

self.event\_queue.put(event) # Añade un evento a la cola de

prioridad.

logger.info(f'Event added: {event.event\_type}, Priority: {event.priority}') # Registra el evento añadido.

async def process\_events(self):![](Aspose.Words.99abc9e3-1440-4111-b872-d984b22e75fe.003.png)

while True:

if not self.event\_queue.empty(): # Verifica si la cola de eventos no está vacía.

with self.lock: # Adquiere el bloqueo antes de obtener un evento de la cola.

event = self.event\_queue.get() # Obtiene el próximo evento de la cola de prioridad.

await self.handle\_event(event) # Maneja el evento obtenido de manera asíncrona.

await asyncio.sleep(0.1) # Pequeña pausa para evitar sobrecargar la CPU.

async def handle\_event(self, event):

if event.event\_type == EventType.CELL\_EXECUTION: # Si el evento es de tipo CELL\_EXECUTION.

await self.execute\_cell(event.data) # Ejecuta la celda asociada al evento de manera asíncrona.

elif event.event\_type == EventType.USER\_INPUT: # Si el evento es de tipo USER\_INPUT.

self.process\_user\_input(event.data) # Procesa la entrada de usuario asociada al evento.

elif event.event\_type == EventType.SYSTEM\_UPDATE: # Si el evento es de tipo SYSTEM\_UPDATE.

self.system\_update(event.data) # Procesa la actualización del sistema asociada al evento.

elif event.event\_type == EventType.ERROR: # Si el evento es de tipo ERROR.

self.handle\_error(event.data) # Maneja el error asociado al evento.

async def execute\_cell(self, cell\_code):

try:

logger.info(f'Executing cell: {cell\_code}') # Registra la ejecución de la celda.

loop = asyncio.get\_running\_loop() # Obtiene el ciclo de eventos en ejecución.

await loop.run\_in\_executor(self.executor, exec, cell\_code)

- Ejecuta la celda en el executor de hilos.

logger.info('Cell execution complete') # Registra la finalización de la ejecución de la celda.

except Exception as e:

logger.error(f'Error executing cell: {e}') # Registra un error si ocurre al ejecutar la celda.![ref1]

self.add\_event(Event(EventType.ERROR, data=str(e), priority=0)) # Añade un evento de error a la cola.

def process\_user\_input(self, user\_input):

logger.info(f'Processing user input: {user\_input}') # Registra el procesamiento de la entrada de usuario.

- Aquí se procesaría la entrada del usuario (implementación

simulada).

def system\_update(self, update\_info): logger.info(f'Performing system update: {update\_info}') #

Registra la actualización del sistema.

- Aquí se procesaría la actualización del sistema

(implementación simulada).

def handle\_error(self, error\_message):

logger.error(f'Handling error: {error\_message}') # Registra el manejo de un error.

- Aquí se manejarían los errores (implementación simulada).

#En este caso se realiza la simulación de un notebook interactivo class NotebookSimulator:

def \_\_init\_\_(self):

self.event\_system = EventSystem() # Inicializa el sistema de eventos.

async def run(self):

event\_task = asyncio.create\_task(self.event\_system.process\_events()) # Crea una tarea para procesar eventos.

- Agrega algunos eventos para simular interacciones de usuario. self.event\_system.add\_event(Event(EventType.USER\_INPUT,

data="User input example", priority=2))

self.event\_system.add\_event(Event(EventType.CELL\_EXECUTION, data="print('Hello, Jupyter!')", priority=1))

self.event\_system.add\_event(Event(EventType.SYSTEM\_UPDATE, data="System update info", priority=3))

await asyncio.sleep(5) # Simula el tiempo de ejecución del notebook.

event\_task.cancel() # Cancela la tarea de procesamiento de eventos.

try:![](Aspose.Words.99abc9e3-1440-4111-b872-d984b22e75fe.004.png)

await event\_task # Espera a que la tarea de procesamiento de eventos termine.

except asyncio.CancelledError:

logger.info("Event processing task cancelled") # Registra la cancelación de la tarea de eventos.

if \_\_name\_\_ == "\_\_main\_\_":

simulator = NotebookSimulator() # Crea una instancia del simulador de notebook.

asyncio.run(simulator.run()) # Ejecuta el simulador utilizando asyncio para manejar la ejecución asíncrona.

[ref1]: Aspose.Words.99abc9e3-1440-4111-b872-d984b22e75fe.002.png
