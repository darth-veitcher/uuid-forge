# UUID Forge

## Purpose and Vision

Deterministic UUID generation for cross-system coordination. The architecture separates development tools, application services, and host concerns into distinct, secure layers with carefully designed network boundaries.

### Core Objectives

- **Complete Host Isolation**: Zero development dependencies or services installed on the host machine
- **Network Segmentation**: Isolated networks preventing cross-contamination between development tools and application services
- **Transparent Operations**: Standard Docker Compose commands only - no custom shell scripts or opaque abstractions
- **Professional Development Experience**: Full VS Code integration with MCP (Model Context Protocol) services for AI-assisted development
- **Security-First Design**: Multiple layers of isolation with principle of least privilege

## Quickstart (5 minutes)

Get up and running with this AI-powered development environment in under 5 minutes.

### Prerequisites

- [ ] Docker Desktop installed and running
- [ ] VS Code with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [ ] Git for cloning the repository

### Steps

1. **Clone and Open**

   ```bash
   git clone https://github.com/darthveitcher/uuid-forge.git
   cd uuid-forge
   code .
   ```

2. **Start Development Environment**

   - VS Code will detect `.devcontainer` and prompt "Reopen in Container"
   - Click "Reopen in Container" (or use Command Palette: `Dev Containers: Reopen in Container`)
   - First-time setup builds the container (2-3 minutes)

3. **Verify Everything is Running**

   ```bash
   # In the VS Code terminal (inside container)
   docker compose ps  # Should show all services healthy
   ```

4. **Start Using Claude**

   ```bash
   # Claude CLI is pre-configured with all MCP services
   claude "explain the architecture of this project"
   claude "help me add a new API endpoint"
   ```

5. **Access Your Application**
   - Run `docker compose -f app/compose.yml up -d`
   - Open http://localhost:8000 in your browser
   - The FastAPI application is now running with hot-reload enabled

That's it! You're now running a fully isolated development environment with AI assistance.

### Next Steps

- Run `claude "show me what MCP services are available"` to explore AI capabilities
- Check the [Development Workflow](#development-workflow) section for detailed usage
- See [MCP Services Integration](#mcp-services-integration) for available AI tools

## Architecture Overview

### Four-Layer Design

1. **Host Machine** - Provides Docker runtime only, remains completely clean
2. **Development Environment** - VS Code devcontainer with development tools and AI services
3. **Development Services** - MCP servers, search engines, and development utilities
4. **Application Stack** - Your actual application with isolated database and caching

### Network Topology

```
┌─────────────────┐    ┌─────────────────┐
│   Host Machine  │    │  External Web   │
│   (Docker only) │    │   (port 8000)   │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       │
┌─────────────────────────────────────────┐
│           Shared Network                │
│  ┌─────────────────┐  ┌───────────────┐ │
│  │  Devcontainer   │  │  Application  │ │
│  │                 │  │     :8000     │ │
│  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────┘
         │                       │
         │                       │
┌─────────────────┐    ┌─────────────────┐
│  Dev-Tools Net  │    │  App Network    │
│   (internal)    │    │   (internal)    │
│                 │    │                 │
│ • SearxNG       │    │ • PostgreSQL    │
│ • Crawl4AI      │    │ • Redis         │
│ • Context7      │    │                 │
│ • Redis/Valkey  │    │                 │
└─────────────────┘    └─────────────────┘
```

## Technology Stack

### Development Environment

- **Base**: Python 3.12 slim container with VS Code Dev Containers
- **Package Management**: FastAPI with standard pip (UV integration available)
- **Container Runtime**: Docker-in-Docker for application stack management

### MCP (Model Context Protocol) Services

- **SearxNG**: Self-hosted search engine for private web search
- **Crawl4AI**: AI-powered web crawling and content extraction
- **Context7**: Codebase documentation and context service
- **Sequential Thinking**: Structured reasoning and analysis tools
- **Serena**: IDE assistant for development workflows
- **Memgraph**: Graph database with MAGE algorithms for complex data relationships
- **Docker**: Container management and orchestration
- **Playwright**: Browser automation and testing
- **Magic**: UI component generation from 21st.dev

### Application Services

- **Web Framework**: FastAPI with Uvicorn server
- **Database**: PostgreSQL 15 with isolated networking
- **Caching**: Redis (separate from development Redis)

## Core Design Principles

### 1. No Custom Shell Scripts

**Principle**: Use standard tooling without custom abstractions.

**Rationale**: Shell scripts create opaque, brittle abstractions over standard tools. They become maintenance burdens and make debugging harder.

**Implementation**: All operations use standard Docker Compose commands:

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Execute commands
docker compose exec service-name command
```

### 2. Network Isolation by Design

**Principle**: Each layer operates on isolated networks with explicit connectivity.

**Networks**:

- `dev-tools` (internal): MCP services isolated from external access
- `shared`: Connects devcontainer and application for communication
- `app-network` (internal): Application's private data services

### 3. Configuration Over Code

**Principle**: Declarative YAML configuration instead of imperative scripts.

**Benefits**:

- Version controlled configuration
- Predictable behavior
- Standard Docker Compose patterns
- Easy to understand and modify

### 4. Security Through Isolation

**Principle**: Multiple layers of isolation prevent unauthorized access.

**Implementation**:

- Development services: No external ports, internal network only
- Application data: Isolated to application containers only
- Host access: Only application port 8000 exposed

## Repository Structure

```
├── .devcontainer/
│   ├── compose.yml              # Development services orchestration
│   ├── devcontainer.json        # VS Code Dev Container configuration
│   ├── Dockerfile               # Development environment image
│   └── mcp/                     # MCP service configurations
│       ├── crawl4ai/
│       ├── searxng/
│       ├── context7/
│       └── memgraph-ai-toolkit/ # Memgraph MCP server (submodule)
├── app/
│   ├── compose.yml              # Application stack orchestration
│   ├── Dockerfile               # Application container image
│   ├── main.py                  # FastAPI application
│   └── requirements.txt         # Python dependencies
├── .mcp.json                    # MCP server configuration for Claude
├── .gitmodules                  # Git submodules for MCP services
└── README.md                    # This documentation
```

## Development Workflow

### Initial Setup

1. **Prerequisites**: Docker Desktop and VS Code with Dev Containers extension
2. **Open Repository**: VS Code automatically detects and offers to open in container
3. **Container Build**: First-time setup builds development environment (2-3 minutes)
4. **Service Startup**: MCP services start automatically with health checks

### Daily Development

```bash
# Services start automatically when opening devcontainer

# Start application stack
cd app
docker compose up -d

# View application logs
docker compose logs -f app

# Access application shell
docker compose exec app bash

# Test MCP services (from devcontainer terminal)
curl http://searxng:8080               # Search engine
curl http://crawl4ai:11235             # AI web crawler
nc -zv memgraph 7687                   # Memgraph database
curl http://memgraph-lab:3000          # Memgraph Lab UI
```

### Application Access

- **From Host**: http://localhost:8000
- **From Devcontainer**: http://app:8000
- **Health Check**: http://localhost:8000/health

## MCP Services Integration

### SearxNG (Private Search)

- **Purpose**: Self-hosted search engine for private web searches
- **Access**: http://devenv-searxng:8080 (devcontainer only)
- **Configuration**: Privacy-focused with no external tracking

### Crawl4AI (Web Intelligence)

- **Purpose**: AI-powered web crawling and content extraction
- **Access**: http://devenv-crawl4ai:11235 (devcontainer only)
- **Features**: LLM-powered content analysis and extraction

### Context7 (Codebase Documentation)

- **Purpose**: Automated codebase documentation and context
- **Access**: http://devenv-mcp-context7:8080 (devcontainer only)
- **Integration**: Provides repository context to AI assistants

### Memgraph (Graph Database)

- **Purpose**: Graph database with MAGE algorithms for complex data relationships
- **Database Access**: bolt://memgraph:7687 (Bolt protocol)
- **Web UI**: http://memgraph-lab:3000 (Visual graph exploration)
- **Features**: Cypher queries, graph algorithms (PageRank, centrality), schema management

## Security Model

### Access Control Matrix

| Service        | Host Access       | Devcontainer Access | App Container Access |
| -------------- | ----------------- | ------------------- | -------------------- |
| Application    | ✅ Port 8000      | ✅ http://app:8000  | N/A                  |
| SearxNG        | ✅ Port 8080      | ✅ Internal network | ❌                   |
| Crawl4AI       | ✅ Port 11235     | ✅ Internal network | ❌                   |
| Context7       | ❌                | ✅ Internal network | ❌                   |
| Memgraph       | ❌                | ✅ Internal network | ❌                   |
| Memgraph Lab   | ✅ Port 3000      | ✅ Internal network | ❌                   |
| App PostgreSQL | ❌                | ❌                  | ✅ Internal only     |
| App Redis      | ❌           | ❌                  | ✅ Internal only     |

### Security Boundaries

1. **Host Isolation**: No development services accessible from host
2. **Network Segmentation**: MCP services cannot access application data
3. **Service Isolation**: Application data services isolated from development tools
4. **Container Security**: Non-root users, minimal attack surface

## Operational Commands

### Service Management

```bash
# View all running containers
docker compose ps

# Stop all services
docker compose down

# Restart specific service
docker compose restart service-name

# View service logs
docker compose logs -f service-name

# Execute commands in service
docker compose exec service-name bash
```

### Application Development

```bash
# Start application stack
cd app && docker compose up -d

# Hot reload development
cd app && docker compose up --watch

# Run tests
cd app && docker compose exec app python -m pytest

# Database access
cd app && docker compose exec postgres psql -U appuser -d appdb
```

### Debugging and Troubleshooting

```bash
# Check service health
docker compose ps

# Inspect networks
docker network ls
docker network inspect devcontainer_dev-tools

# View resource usage
docker stats

# Clean up resources
docker system prune -f
```

## Development Patterns

### Adding MCP Services

1. Add service to `.devcontainer/compose.yml` on `dev-tools` network
2. Configure in `.mcp.json` for Claude integration
3. Use `expose` not `ports` to maintain isolation
4. Add health checks for reliable startup

### Scaling Application Services

1. Add services to `app/compose.yml` on `app-network`
2. Use internal networking for data services
3. Only expose application ports to `shared` network
4. Maintain database isolation principles

### Environment Configuration

- **Development**: Service discovery via Docker DNS
- **Production**: External service configuration
- **Testing**: Isolated test databases and services

## Benefits and Trade-offs

### Benefits

- **Security**: Multiple isolation layers prevent unauthorized access
- **Consistency**: Identical environments across all developers
- **Productivity**: Rich AI assistance through MCP services
- **Maintainability**: Standard tools, no custom scripts
- **Scalability**: Easy to add services or team members

### Trade-offs

- **Complexity**: Multi-network setup requires Docker knowledge
- **Resources**: Multiple containers consume more system resources
- **Startup Time**: Initial container builds take 2-3 minutes
- **Platform Dependency**: Requires Docker Desktop and VS Code

## Future Enhancements

### Planned Improvements

- **UV Integration**: Faster Python dependency management
- **Multi-stage Builds**: Optimized container images
- **Health Dashboards**: Service monitoring and alerting
- **CI/CD Integration**: Automated testing and deployment

### Extension Points

- **Additional MCP Services**: Easy to add new AI tools
- **Database Options**: Support for MongoDB, MySQL, etc.
- **Language Support**: Extend to other development stacks
- **Cloud Integration**: Deployment to container orchestration platforms

## Contributing and Customization

### Customizing for Your Needs

1. **Fork the repository** and modify service configurations
2. **Add your MCP services** to the dev-tools network
3. **Configure your application stack** in the app directory
4. **Update .mcp.json** for Claude integration

### Best Practices

- Maintain network isolation principles
- Use standard Docker Compose patterns
- Document any custom configurations
- Test across platforms (Windows, macOS, Linux)

---

**This repository represents a production-ready approach to containerized development that prioritizes security, maintainability, and developer experience while avoiding the complexity and brittleness of custom shell scripts.**
