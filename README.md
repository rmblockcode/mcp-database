# 🏦 Sistema de Gestión de Préstamos - Servidor MCP

Sistema de gestión de préstamos bancarios implementado como servidor MCP (Model Context Protocol) con FastMCP, PostgreSQL y SQLAlchemy.

## 📋 Descripción

Este proyecto proporciona un servidor MCP que permite gestionar préstamos bancarios y sus cuotas asociadas. Utiliza una arquitectura asíncrona con PostgreSQL como base de datos y expone herramientas MCP para consultar información de préstamos, clientes y cuotas de pago.

## 🎥 Video Tutorial

📺 **[Ver clase completa en YouTube](https://www.youtube.com/TU_VIDEO_AQUI)**

En este video se explica paso a paso la implementación del servidor MCP, la arquitectura del proyecto, y cómo integrar PostgreSQL con FastMCP.

## ✨ Características

- 🔄 **Arquitectura Asíncrona**: Implementación completamente asíncrona con asyncio y asyncpg
- 🗄️ **Base de Datos PostgreSQL**: Almacenamiento robusto y escalable
- 🛠️ **Servidor MCP**: Exposición de herramientas mediante Model Context Protocol
- 🐳 **Dockerizado**: Despliegue sencillo con Docker Compose
- 📊 **Gestión de Préstamos**: Seguimiento completo de préstamos y cuotas
- 🔍 **Consultas Optimizadas**: Índices y queries optimizadas con SQLAlchemy

## 🏗️ Arquitectura

```
mcp-database/
├── src/
│   ├── __init__.py
│   ├── database.py      # Configuración de base de datos y pool de conexiones
│   ├── models.py        # Modelos SQLAlchemy (Loan, LoanInstallment)
│   ├── tools.py         # Herramientas MCP expuestas
│   └── utils.py         # Utilidades auxiliares
├── server.py            # Punto de entrada del servidor
├── docker-compose.yml   # Orquestación de servicios
├── Dockerfile           # Imagen del servidor MCP
└── pyproject.toml       # Dependencias del proyecto
```

## 🗃️ Modelos de Datos

### Loan (Préstamo)
- `id`: Identificador único del préstamo
- `customer_id`: ID del cliente
- `customer_name`: Nombre del cliente
- `loan_amount`: Monto del préstamo
- `interest_rate`: Tasa de interés
- `loan_term_months`: Plazo en meses
- `start_date`: Fecha de inicio
- `status`: Estado (active, paid, defaulted)
- `remaining_balance`: Saldo pendiente

### LoanInstallment (Cuota)
- `id`: Identificador único de la cuota
- `loan_id`: ID del préstamo asociado
- `installment_number`: Número de cuota
- `due_date`: Fecha de vencimiento
- `amount_due`: Monto a pagar
- `principal_amount`: Monto del capital
- `interest_amount`: Monto de intereses
- `amount_paid`: Monto pagado
- `payment_date`: Fecha de pago
- `status`: Estado (pending, paid, overdue, partial)

## 🛠️ Herramientas MCP Disponibles

### 1. `get_customer_loans`
Obtiene todos los préstamos de un cliente específico.

**Parámetros:**
- `customer_id` (str): ID único del cliente (ej: CUST001)

**Retorna:** Lista de préstamos con todos sus detalles (ID, monto, tasa de interés, plazo, estado, saldo pendiente)

### 2. `get_all_customers`
Obtiene la lista de todos los clientes en el sistema.

**Retorna:** Lista de clientes con sus IDs y nombres ordenados alfabéticamente

### 3. `get_loan_installments`
Obtiene todas las cuotas de un préstamo específico.

**Parámetros:**
- `loan_id` (int): ID único del préstamo

**Retorna:** Detalles del préstamo y lista completa de cuotas ordenadas por número de cuota

### 4. `get_pending_installments`
Obtiene todas las cuotas pendientes de pago para un préstamo específico.

**Parámetros:**
- `loan_id` (int): ID único del préstamo

**Retorna:** Lista de cuotas con estado "pending", "overdue" o "partial", incluyendo el monto total pendiente

**Casos de uso:**
- Verificar cuánto debe pagar un cliente en un préstamo específico
- Identificar próximos vencimientos
- Calcular el total pendiente de pago

### 5. `get_overdue_installments`
Obtiene todas las cuotas vencidas de un cliente a través de todos sus préstamos.

**Parámetros:**
- `customer_id` (str): ID único del cliente

**Retorna:** Lista de todas las cuotas vencidas del cliente, monto total vencido, cantidad de cuotas vencidas y días de atraso

**Casos de uso:**
- Identificar clientes morosos
- Calcular penalidades por atraso
- Generar reportes de cobranza

### 6. `get_customer_summary`
Obtiene un resumen completo y detallado de un cliente buscando por nombre.

**Parámetros:**
- `customer_name` (str): Nombre del cliente (soporta búsqueda parcial)

**Retorna:** Resumen completo incluyendo:
- Información del cliente (ID y nombre)
- Estadísticas generales:
  - Total de préstamos y préstamos activos
  - Monto total prestado
  - Saldo pendiente total
  - Total pagado
  - Monto pendiente de pago
  - Monto vencido
  - Cantidad de cuotas vencidas y pendientes
- Detalles de cada préstamo

**Casos de uso:**
- Vista 360° del cliente
- Evaluación de riesgo crediticio
- Análisis de comportamiento de pago
- Reportes ejecutivos

## 🚀 Instalación y Uso

### Prerrequisitos

- Docker y Docker Compose
- Python 3.14+ (para desarrollo local)

### Despliegue con Docker Compose

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd mcp-database
```

2. **Configurar variables de entorno (opcional)**

Crear un archivo `.env` en la raíz del proyecto:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=loans_db
POSTGRES_PORT=5432
POOL_SIZE=20
DATABASE_ECHO=False
```

3. **Iniciar los servicios**
```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL en el puerto 5432
- Servidor MCP en el puerto 8000

4. **Verificar el estado**
```bash
docker-compose ps
docker-compose logs -f mcp_server
```

### Desarrollo Local

1. **Instalar dependencias**
```bash
pip install -e .
```

2. **Configurar la base de datos**
```bash
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost:5432/loans_db"
```

3. **Ejecutar el servidor**
```bash
python server.py
```

## 🔧 Configuración

### Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql+asyncpg://postgres:password@postgres:5432/loans_db` |
| `POOL_SIZE` | Tamaño del pool de conexiones | `20` |
| `DATABASE_ECHO` | Habilitar logs de SQL | `False` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `password` |
| `POSTGRES_DB` | Nombre de la base de datos | `loans_db` |

### Pool de Conexiones

El servidor utiliza un pool de conexiones asíncrono configurado con:
- Pool size: 20 conexiones
- Max overflow: 10 conexiones adicionales
- Pool timeout: 30 segundos
- Pool recycle: 3600 segundos

## 📡 API del Servidor

El servidor MCP expone sus herramientas mediante Server-Sent Events (SSE) en:

```
http://localhost:8000
```

### Logs del servidor
```bash
docker-compose logs -f mcp_server
```

## 👥 Autores

- Desarrollado con  ❤️ por [@rmblockcode](https://www.instagram.com/rmblockcode)
