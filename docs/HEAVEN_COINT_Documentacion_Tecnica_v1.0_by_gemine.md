# **Documento de Arquitectura de Software: Orion One**

## **1\. Análisis profundo del producto**

* **Propósito central del software:** Proporcionar una plataforma de análisis cuantitativo y diseño de estrategias de trading en tiempo real, utilizando un motor matemático determinista acoplado a un asistente de Inteligencia Artificial especializado.  
* **Problema que resuelve:** La ineficacia de los LLMs genéricos (como ChatGPT) en el trading. Los traders minoristas pierden dinero al confiar en IAs que "alucinan" consejos financieros basándose en textos estáticos de internet, ignorando el flujo de órdenes en tiempo real, la volatilidad implícita y la gestión matemática del riesgo.  
* **Usuarios objetivo y sus necesidades:**  
  * *Traders minoristas (Retail):* Necesitan acceso a análisis de nivel institucional sin la complejidad de programar modelos cuantitativos.  
  * *Traders intermedios/avanzados:* Requieren optimizar su esperanza matemática mediante confluencia de señales y estandarización del tamaño de posición.  
* **Valor diferencial:**  
  * *IA Determinista (Context-Bound):* El asistente no busca en internet; solo procesa una matriz de KPIs financieros (ATR, Proyecciones, Volatilidad) inyectada en tiempo real.  
  * *Indicadores Propietarios:* "Oscilador NetBrute" (flujo real de órdenes/dinero inteligente) y "Oscilador de Intenciones" (psicología de masas/sentimiento).  
  * *Gestión Cuantitativa Estricta:* Cálculo automatizado de Stop Loss (SL) dinámico, Take Profits (TP) escalonados y dimensionamiento de posición (Position Sizing).  
* **Alcance actual y potencial de crecimiento:**  
  * *Actual:* Herramienta SaaS de análisis (Dashboard \+ Chatbot cuantitativo).  
  * *Potencial:* Integración de webhooks para ejecución automatizada (ej. vía n8n hacia brokers), backtesting integrado, y gestión de portafolios multi-activo.

---

## **2\. Ciclo de vida del diseño del software (SDLC)**

* **Fase de requerimientos (Inferidos):** Ingesta de datos de mercado en tiempo real (Nivel 1 y Nivel 2/Order Book), análisis de sentimiento en tiempo real, latencia ultrabaja para la actualización de KPIs, y respuestas del LLM en menos de 3-5 segundos.  
* **Fase de diseño (Arquitectura propuesta):** Arquitectura orientada a eventos (EDA) para el flujo de datos de mercado, combinada con un patrón *Backend-for-Frontend (BFF)* para servir a la UI. Separación estricta entre el motor matemático y el motor LLM.  
* **Fase de desarrollo (Metodología sugerida):** Desarrollo iterativo basado en *Vertical Slicing*. Primer slice: Ingesta de un solo activo (ej. AAPL) \-\> Cálculo de ATR y NetBrute \-\> Prompting determinista \-\> UI.  
* **Fase de pruebas (Estrategia de testing):**  
  * *Unit Testing:* Cobertura del 100% en el motor matemático. Un error en el cálculo del tamaño de posición cuesta dinero real.  
  * *Evaluación de IA (Eval):* Pruebas automatizadas contra el LLM inyectando escenarios límite (ej. alta volatilidad) para asegurar que nunca alucine ni recomiende operar sin confirmación.  
* **Fase de despliegue (Entornos):** Contenedorización completa. Entornos separados de Staging (conectado a *paper trading* y datos retrasados) y Producción (datos en vivo).  
* **Fase de mantenimiento:** Monitoreo intensivo (ej. Netdata, Prometheus) de los *rate limits* de la API del LLM y de los proveedores de datos financieros.

---

## **3\. Stack tecnológico recomendado**

Considerando un perfil de ingeniería moderno y la necesidad de cálculos cuantitativos:

* **Frontend:**  
  * **Framework:** React con TypeScript. Tipado estricto es obligatorio para datos financieros.  
  * **Estado & Data Fetching:** Zustand (estado global ligero) y React Query (caché y sincronización de datos asíncronos).  
  * **Visualización:** Lightweight Charts (de TradingView) para gráficos de velas de alto rendimiento. TailwindCSS para el diseño UI.  
* **Backend:**  
  * **Lenguaje/Framework:** Python 3.11+ con **FastAPI**. Python es el rey indiscutible en finanzas cuantitativas, librerías matemáticas (NumPy/Pandas) e IA. FastAPI proporciona alto rendimiento asíncrono.  
* **Base de datos:**  
  * **Series de Tiempo:** TimescaleDB (PostgreSQL) o InfluxDB para almacenar el histórico de ticks, precios y valores de los osciladores.  
  * **Caché en Memoria:** Redis. Esencial para servir los KPIs actuales al dashboard con latencia \< 50ms.  
  * **Relacional:** PostgreSQL para gestión de usuarios, perfiles de riesgo y registro de estrategias generadas.  
* **Infraestructura:**  
  * **Contenedores:** Docker y orquestación con Docker Compose o Portainer para despliegues ágiles en servidores VPS o Cloud.  
  * **Proxy Inverso:** Traefik para enrutamiento dinámico y gestión de certificados SSL automáticos.  
* **Servicios externos:**  
  * **Market Data:** Polygon.io o Alpaca API (para acciones/crypto en tiempo real).  
  * **LLM Provider:** OpenAI (GPT-4o) o modelos locales alojados en Ollama (como Llama 3\) para privacidad total y reducción de costos recurrentes.  
* **Justificación:** Este stack separa la carga pesada de cálculos (Python/Pandas) de la interactividad en tiempo real (FastAPI/React/Redis), siendo fácilmente empaquetable en contenedores.

---

## **4\. Arquitectura de módulos**

La arquitectura se divide en 5 módulos principales operando de forma asíncrona.

* **Módulo de Ingesta (Data Feeder):** Conecta vía WebSockets a proveedores externos. Limpia y normaliza datos (OHLCV, Order Book).  
* **Motor Cuantitativo (Quant Engine):** Recibe datos normalizados. Calcula ATR, medias móviles, volatilidad implícita y ejecuta la lógica propietaria de los osciladores NetBrute e Intenciones. Actualiza Redis constantemente.  
* **Gestor de Riesgo (Risk Manager):** Evalúa el capital del usuario y calcula variables críticas mediante fórmulas matemáticas: Tamaño de posición $N \= \\frac{\\text{Capital} \\times \\text{Riesgo}}{\\text{Precio} \- \\text{SL}}$ y niveles de Take Profit.  
* **Orquestador de IA (AI Agent Service):** Toma el "Snapshot" actual de Redis (los KPIs) y el perfil de riesgo, construye el *System Prompt* determinista y se comunica con el LLM.  
* **API Gateway:** Interfaz REST/WebSocket para el Frontend.

### **Diagrama Conceptual (Mermaid)**

graph TD  
    subgraph Fuentes Externas  
        MD\[Market Data API\]  
        NLP\[News/Social Sentiment\]  
        LLM\[OpenAI / Ollama\]  
    end

    subgraph Orion One Backend  
        Ingesta\[Data Ingestion Service\]  
        QE\[Motor Cuantitativo \- Pandas/NumPy\]  
        RM\[Gestor de Riesgo Matemático\]  
        Redis\[(Redis \- Estado Actual)\]  
        TSDB\[(TimescaleDB \- Histórico)\]  
        AI\[Agente Orquestador IA\]  
        API\[FastAPI Gateway\]  
    end

    subgraph Frontend Client  
        Dash\[Dashboard UI\]  
        Chat\[Chatbot Interface\]  
    end

    MD \-- WebSockets \--\> Ingesta  
    NLP \--\> Ingesta  
    Ingesta \--\> QE  
    QE \--\> TSDB  
    QE \--\> Redis  
      
    Dash \-- Polling/WS \--\> API  
    API \-- Lee KPIs \--\> Redis  
      
    Chat \-- "Prompt del Usuario" \--\> API  
    API \--\> AI  
    AI \-- "Lee Contexto" \--\> Redis  
    AI \-- "Valida Riesgo" \--\> RM  
    AI \-- "Prompt Inyectado" \--\> LLM  
    LLM \--\> AI  
    AI \--\> Chat  
5\. Modelo de datos (Entidades principales

| Entidad | Descripción | Atributos Críticos | Reglas / Validaciones |
| :---- | :---- | :---- | :---- |
| **User** | Información del trader. | id, capital\_base, max\_risk\_pct (ej. 1%). | El riesgo nunca debe exceder el 5% por sistema. |
| **AssetSnapshot** | Estado de los KPIs en un segundo $T$. | symbol, price, atr, netbrute\_val, intentions\_val, volatility\_trend. | Almacenado en Redis con TTL (Time-to-Live) corto. |
| **TradeStrategy** | El plan generado por la IA. | asset, entry\_price, stop\_loss, tp\_1, tp\_2, position\_size, status. | stop\_loss debe calcularse como $\\text{Precio} \- (2.5 \\times ATR)$. |
| **ConfluenceRule** | Reglas para nivel 2 de estrategias. | oscillator\_state, price\_action\_trend, macro\_alignment. | Debe cumplirse \> 3 reglas para aprobar "Confluencia". |

## **6\. Flujos de trabajo clave**

**Flujo de Generación de Estrategia Segura:**

1. **Solicitud:** El usuario pide a la IA: "Diseña estrategia de compra para Apple".  
2. **Recolección de Contexto:** El *AI Agent Service* consulta a Redis los KPIs actuales de AAPL (Precio: 272.95, ATR: 3.27, NetBrute: \-35.53, etc.) y consulta el perfil del usuario (Capital: 10,000, Riesgo: 1%).  
3. **Evaluación de Divergencia:** El sistema detecta lógicamente si el Oscilador de Intenciones vs. NetBrute están en direcciones opuestas.  
4. **Inyección Determinista:** El Backend arma el Prompt. *Ejemplo interno: "Eres un analista. El usuario quiere comprar. Los datos son \[KPIs\]. El riesgo máximo es 100\. Calcula TPs basados en 1.5x y 2.5x ATR. Si hay divergencia, advierte."*  
5. **Respuesta:** La IA formatea el texto. El Backend intercepta la respuesta, extrae los valores numéricos y los renderiza en la UI como tarjetas estructuradas interactivas.

**Casos de borde identificados:**

* *Fallo del proveedor de datos:* Si el ATR no se puede calcular por falta de velas, el sistema debe bloquear la generación de estrategias (Fail-Safe).  
* *Volatilidad extrema (Cisne Negro):* Si el ATR se expande en más de un 300% respecto a su media histórica, el tamaño de la posición tenderá a cero. El sistema debe sugerir "No operar".

---

## **7\. Requisitos no funcionales**

* **Escalabilidad:** Separar los "Workers" que calculan los osciladores del "Gateway" que sirve a los usuarios. Si se añaden más criptomonedas o acciones, escalar los workers horizontalmente.  
* **Seguridad:** Validación robusta en el *Gestor de Riesgo*. La IA propone, pero una capa de validación en código duro debe asegurar que la matemática del Stop Loss sea correcta antes de mostrarla al usuario.  
* **Rendimiento:** La consulta de KPIs por parte del LLM no debe penalizar el tiempo de respuesta. El acceso a Redis garantiza lecturas de $\< 5 \\text{ms}$.  
* **Disponibilidad:** Arquitectura resiliente. Si el LLM principal (ej. OpenAI) se cae, debe existir un *fallback* automático a otro proveedor (ej. Anthropic) o un LLM local.

---

## **8\. Recomendaciones estratégicas**

* **Riesgos técnicos identificados:**  
  * *La "Caja Negra" de los Osciladores:* El documento menciona el "NetBrute" y el "Oscilador de Intenciones". Construir algoritmos precisos que procesen *Order Flow* institucional y *Sentiment Analysis* en tiempo real es extremadamente complejo y costoso en computación. Será el principal cuello de botella.  
* **Deuda técnica potencial:**  
  * Depender exclusivamente del LLM para hacer los cálculos matemáticos en el texto. **Solución:** Que el backend de Python realice la matemática estricta (ATR, Position Sizing) y el LLM solo se use para *explicar* la estrategia, nunca para calcularla.  
* **Mejoras Futuras (Automatización via Webhooks):**  
  * Integrar herramientas de flujos de trabajo (como n8n) para que, una vez la IA genere la estrategia y el usuario le dé clic a "Aprobar", un webhook dispare la orden de compra directamente al broker (API de Binance, Interactive Brokers, etc.), cerrando el ciclo de automatización.  
* **Alternativas de arquitectura (Privacidad/Costos):**  
  * Para aislar los datos financieros del usuario y reducir latencia, se puede implementar un servidor VPS potente e instalar modelos de inferencia locales mediante Ollama. Un modelo pequeño y afinado (fine-tuned) para tareas financieras específicas sería mucho más rápido y seguro que GPT-4.

