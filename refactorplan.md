# Plan de Refactor: BrightData MCP Agent

## Resumen del Proyecto Actual
El proyecto actual es un agente conversacional que utiliza:
- LangGraph con Claude (Anthropic)
- MCP (Model Context Protocol) para herramientas de BrightData
- UV como gestor de paquetes
- Interfaz básica de terminal

## Objetivos del Refactor

### 1. Migración de UV a pip
- Convertir `pyproject.toml` a `requirements.txt` + `setup.py`
- Usar `venv` estándar para entornos virtuales
- Mantener compatibilidad con Python 3.8+

### 2. Migración de Claude a OpenAI
- Reemplazar `ChatAnthropic` con `ChatOpenAI`
- Actualizar configuración de API keys
- Mantener funcionalidad de streaming si es necesaria

### 3. Implementación Nativa de MCP Tools
- Crear adaptadores Pydantic para herramientas MCP
- Implementar cliente MCP nativo sin dependencias de LangChain
- Mantener todas las funcionalidades de BrightData

### 4. CLI Moderno con Typer/Rich
- Interfaz CLI interactiva y colorida
- Comandos estructurados y ayuda contextual
- Configuración persistente
- Logging avanzado

## Estructura del Proyecto Refactorizado

```
brightdata-agent/
├── src/
│   ├── brightdata_agent/
│   │   ├── __init__.py
│   │   ├── main.py              # CLI principal
│   │   ├── agent.py             # Agente principal
│   │   ├── config.py            # Configuración
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # Modelos OpenAI
│   │   │   └── schemas.py       # Esquemas Pydantic
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── client.py        # Cliente MCP nativo
│   │   │   ├── tools.py         # Adaptadores de herramientas
│   │   │   └── brightdata.py    # Herramientas específicas BrightData
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py      # Comandos CLI
│   │   │   ├── chat.py          # Comando de chat
│   │   │   └── config.py        # Comando de configuración
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logging.py       # Configuración de logs
│   │       └── helpers.py       # Utilidades
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── README.md
├── .env.example
└── tests/
    ├── __init__.py
    ├── test_agent.py
    ├── test_mcp.py
    └── test_cli.py
```

## Dependencias Nuevas

### Core Dependencies
```
openai>=1.0.0
pydantic>=2.0.0
typer[all]>=0.9.0
rich>=13.0.0
httpx>=0.24.0
asyncio-mqtt>=0.16.0  # Para MCP stdio
python-dotenv>=1.0.0
```

### Development Dependencies
```
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
pre-commit>=3.0.0
```

## Implementación por Fases

### Fase 1: Estructura Base y CLI
1. **Crear nueva estructura de directorios**
2. **Implementar CLI con Typer**
   - Comando `chat`: Modo conversacional
   - Comando `config`: Gestión de configuración
   - Comando `tools`: Listar herramientas disponibles
3. **Sistema de configuración con Pydantic**

### Fase 2: Cliente MCP Nativo
1. **Implementar cliente MCP stdio nativo**
2. **Adaptadores Pydantic para herramientas**
3. **Integración con herramientas BrightData**

### Fase 3: Integración OpenAI
1. **Reemplazar modelo de chat**
2. **Implementar function calling de OpenAI**
3. **Mantener compatibilidad con herramientas MCP**

### Fase 4: Features Avanzadas
1. **Sistema de logging avanzado**
2. **Persistencia de conversaciones**
3. **Configuración de modelos dinámica**
4. **Tests y documentación**

## Detalles de Implementación

### CLI con Typer + Rich
```python
# Ejemplo de interfaz CLI
@app.command()
def chat(
    model: str = typer.Option("gpt-4", help="Modelo OpenAI a usar"),
    temperature: float = typer.Option(0.7, help="Temperatura del modelo"),
    max_tokens: int = typer.Option(4000, help="Máximo de tokens"),
    verbose: bool = typer.Option(False, help="Modo verbose")
):
    """Iniciar una sesión de chat con el agente"""
    # Implementación
```

### Cliente MCP Nativo
```python
class MCPClient:
    """Cliente MCP nativo usando stdio"""
    
    async def connect(self, command: List[str], env: Dict[str, str]):
        """Conectar al servidor MCP"""
        
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Llamar una herramienta MCP"""
        
    async def list_tools(self) -> List[Tool]:
        """Listar herramientas disponibles"""
```

### Adaptadores Pydantic
```python
class BrightDataTool(BaseModel):
    """Modelo base para herramientas BrightData"""
    name: str
    description: str
    parameters: Dict[str, Any]
    
    async def execute(self, **kwargs) -> Any:
        """Ejecutar la herramienta"""
```

### Integración OpenAI
```python
class OpenAIAgent:
    """Agente principal con OpenAI"""
    
    def __init__(self, model: str, tools: List[BrightDataTool]):
        self.client = OpenAI()
        self.model = model
        self.tools = tools
        
    async def chat(self, message: str) -> str:
        """Procesar mensaje del usuario"""
```

## Comandos CLI Propuestos

### Configuración
```bash
# Configurar API keys
brightdata-agent config set openai-key sk-...
brightdata-agent config set brightdata-token ...

# Ver configuración actual
brightdata-agent config show

# Resetear configuración
brightdata-agent config reset
```

### Chat Interactivo
```bash
# Chat básico
brightdata-agent chat

# Chat con parámetros específicos
brightdata-agent chat --model gpt-4 --temperature 0.5 --verbose

# Cargar conversación previa
brightdata-agent chat --load conversation-123
```

### Herramientas
```bash
# Listar herramientas disponibles
brightdata-agent tools list

# Información de una herramienta específica
brightdata-agent tools info search_engine

# Probar una herramienta
brightdata-agent tools test search_engine --query "Python tutorials"
```

## Ventajas del Refactor

### Técnicas
- **Mejor mantenibilidad**: Código más modular y organizado
- **Menos dependencias**: Eliminación de LangGraph y adaptadores específicos
- **Mayor flexibilidad**: Soporte para múltiples modelos OpenAI
- **Testing mejorado**: Estructura que facilita pruebas unitarias

### Experiencia de Usuario
- **CLI intuitivo**: Comandos claros con ayuda contextual
- **Configuración persistente**: No necesidad de reconfigurar constantemente
- **Feedback visual**: Interfaz rica con colores y progress bars
- **Logging detallado**: Mejor debugging y monitoreo

### Compatibilidad
- **Python estándar**: Uso de pip y venv nativos
- **Multiplataforma**: Compatible con Windows, macOS y Linux
- **Versionado semántico**: Mejor gestión de releases

## Cronograma Estimado

- **Semana 1**: Fase 1 - Estructura base y CLI
- **Semana 2**: Fase 2 - Cliente MCP nativo
- **Semana 3**: Fase 3 - Integración OpenAI
- **Semana 4**: Fase 4 - Features avanzadas y testing

Este refactor transformará el proyecto en una herramienta CLI moderna, mantenible y fácil de usar, con todas las funcionalidades originales pero con mejor arquitectura y experiencia de usuario.