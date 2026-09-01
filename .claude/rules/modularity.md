# Claude Code Rule: Modular, Plugin-Oriented Software

Build cohesive, independently understandable modules — like good dumplings on a plate. Each dumpling has a wrapper that keeps its filling to itself (encapsulation), holds its own distinct filling (separation of concerns, a bounded context), can be cooked and tasted on its own (developed and tested separately), and touches its neighbors without sticking (loose coupling). The failure mode is letting the dumplings fuse into one messy clump through hidden imports, shared state, and cross-module shortcuts — then nothing can be changed, developed, or tested separately.

## Core Rules

1. **Choose ownership first.** Before coding, name the module that owns the feature, its public API, and its allowed dependencies. A module owns its domain logic and internals; other modules use only its documented API.

2. **Use ports and plugins.** Core/application code depends on small interfaces (ports/protocols/traits), never concrete databases, vendor SDKs, HTTP clients, queues, file systems, or LLM providers. Put those implementations in replaceable adapter/plugin modules.

3. **Keep dependencies one-way.**
   - Domain/core: business concepts and rules; no framework or infrastructure dependencies.
   - Application: use cases; may depend on domain and abstract ports.
   - Plugins/adapters: implement ports; may use external libraries.
   - Entrypoints/bootstrap: configuration and dependency wiring only.

   Never import infrastructure, UI, framework, ORM, or vendor code into the domain/core.

4. **Make wiring explicit.** Select and construct concrete plugins in a small composition root. Pass dependencies through constructors or function arguments. Do not use service locators, global mutable state, import-time registration, implicit singletons, or monkey-patching.

5. **Protect module boundaries.** Never read/write another module’s private files, persistence, mutable state, or implementation details. Do not expose ORM entities, framework request objects, or vendor types in public contracts. Use typed inputs/outputs with defined errors.

6. **Reject cycles.** Circular imports and module dependencies are design errors. Fix them by moving a contract to a lower-level module, extracting a focused abstraction, restructuring ownership, or using an event/port—not with late/dynamic imports.

7. **Keep modules cohesive.** One clear responsibility per module. Do not create catch-all `utils`, `common`, `helpers`, `shared`, or `models` modules that collect unrelated code. Prefer feature/domain-oriented organization.

8. **Test independently.** Every module must have isolated unit tests using fakes/stubs/mocks for ports and external systems. Give adapters focused integration tests. Reserve end-to-end tests for critical workflows, not ordinary module behavior.

## Required Workflow

Before implementation, state:

- Owning module and public API.
- New or changed port/plugin contracts.
- Dependency direction.
- Unit and integration tests to add.

After implementation, verify:

- No circular or reverse dependencies.
- No access to another module’s internals or persistence.
- New behavior passes isolated module tests.
- A concrete plugin can be replaced without changing core business logic.
- Any exception is documented with its reason, scope, and containment plan.

## Preferred Shape

```text
src/
  domain/         # Business rules, entities, ports
  application/    # Use cases / orchestration
  plugins/        # Database, APIs, queues, LLMs, etc.
  interfaces/     # HTTP, CLI, workers
  bootstrap/      # Configuration and dependency wiring
```

Adapt names to the stack, but preserve ownership and dependency direction.

## Definition of Done

A change is complete only when its owner and public contract are clear; dependency flow is acyclic and inward; external systems are behind adapters; tests run in isolation; concrete plugins are chosen only in the composition root; and no undocumented cross-module coupling exists.

**Principle:** A piece should be changeable, replaceable, testable, or removable without understanding or modifying the whole application.
