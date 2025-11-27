# Echo Nexus Cathedral — Architecture (R1 Unistack)
NestJS backend (URC + REG + Agents + Gateway) ↔ WebSocket/HTTP ↔ React + R3F frontend (Codex UI + reactive world).

## Repo Tree (target)
echo-nexus/
  backend/
    src/
      main.ts
      app.module.ts
      common/
        types/
          urc.types.ts
          narrative.types.ts
          market.types.ts
          reg.types.ts
          resonance.types.ts
      urc/
        urc.config.ts
        urc.module.ts
        urc.service.ts
        urc.controller.ts
      reg/
        reg.module.ts
        reg.service.ts
      resonance/
        resonance.module.ts
        resonance.service.ts
      market/
        market.module.ts
        market.brain.ts
        market.service.ts
      narrative/
        narrative.module.ts
        narrative.service.ts
      agents/
        agents.module.ts
        agents.service.ts
        demo-agents.ts
      gateway/
        gateway.module.ts
        events.gateway.ts
  frontend/
    src/
      index.tsx
      App.tsx
      socket/
        socket.ts
      hooks/
        useURCCodex.ts
        useMarketTelemetry.ts
        useURCImprints.ts
      components/
        CodexTablet.tsx
        MarketReactiveEnvironment.tsx
        LightningMotif.tsx
      types/
        urc-client-types.ts

## Data Flow \
Movie\
1. MarketService ticks → produces marketTelemetry
2. NarrativeService computes tension → narrativeTension
3. URCService evaluates triggers → HybridTriggerEvent[]
4. URCService builds swarm plans → SwarmActivationPlan
5. AgentsService runs swarm → EvolutionImprint
6. REGService appends imprint (history / graph spine)
7. Gateway emits:
   - telemetry:update { marketTelemetry, narrativeTension }
   - urc:imprint EvolutionImprint
   - urc:codex on connect

Frontend:
8. socket.ts maintains ONE connection
9. Hooks subscribe to events
10. R3F components react to telemetry + imprints (lighting, fog, motifs)
11. CodexTablet renders codex + authority chain in-world

## How to run (minimum)
Backend:
- runs on http://localhost:3001
- websocket is socket.io on same origin

Frontend:
- runs on http://localhost:3000
- connects to backend via socket.io + HTTP fallback

Recommended dev order:
1) start backend
2) start frontend
3) open browser → confirm: CodexTablet populates + telemetry updates

## Operational Invariants
- One socket connection per browser tab (shared by hooks).
- Gateway update loop must not overlap (no async interval pileups).
- REG append is append-only; never mutates existing imprints.
