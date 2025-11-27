/**
 * FILE: src/nexus/SkeletonLabPanel.ECS.tsx
 * DESC: Enhanced Skeleton Lab panel integrated with the ECS.
 *       Demonstrates how the SkeletonLabPanel can work as a Nexus tool
 *       to inspect and modify skeleton entities in the world.
 */

import React from "react";
import { Canvas } from "@react-three/fiber";
// import { OrbitControls } from "@react-three/drei"; // TODO: fix drei import

/**
 * Component that renders a skeleton entity from the ECS world.
 */
interface SkeletonEntityRendererProps {
  world: any;
  entityId: string;
}

export const SkeletonEntityRenderer: React.FC<
  SkeletonEntityRendererProps
> = ({ world, entityId }) => {
  const entity = world.getEntity(entityId);
  if (!entity) {
    return <mesh><boxGeometry args={[0.5, 0.5, 0.5]} /></mesh>;
  }

  const COMPONENT_TYPE = {
    TRANSFORM: "Transform",
    SKELETON: "Skeleton",
    GRAPHICS: "Graphics",
  };

  const transform = world.getComponent(entity.id, COMPONENT_TYPE.TRANSFORM);
  const skeleton = world.getComponent(entity.id, COMPONENT_TYPE.SKELETON);
  const graphics = world.getComponent(entity.id, COMPONENT_TYPE.GRAPHICS);

  const position = transform?.position || [0, 0, 0];
  const rotation = transform?.rotation || [0, 0, 0, 1];

  return (
    <group position={position as any} quaternion={rotation as any}>
      {/* Render skeleton joints */}
      {skeleton?.poses && (
        <>
          {Array.from(skeleton.poses.entries() as IterableIterator<[string, any]>).map(([jointId, euler]) => {
            const [x, y, z] = euler;
            return (
              <group key={jointId} rotation={[x, y, z]}>
                <mesh position={[0, 0.1, 0]}>
                  <sphereGeometry args={[0.05, 16, 16]} />
                  <meshStandardMaterial color="#22c55e" />
                </mesh>
              </group>
            );
          })}
        </>
      )}

      {/* Render mesh */}
      {graphics && (
        <mesh castShadow receiveShadow>
          <boxGeometry args={[0.5, 1.5, 0.3]} />
          <meshStandardMaterial color={graphics.color.slice(0, 3) as any} />
        </mesh>
      )}
    </group>
  );
};

/**
 * Enhanced Skeleton Lab Panel that works with ECS world.
 */
interface SkeletonLabPanelECSProps {
  world: any;
  selectedEntityId?: string;
  onSelectEntity?: (entityId: string) => void;
}

export const SkeletonLabPanelECS: React.FC<SkeletonLabPanelECSProps> = ({
  world,
  selectedEntityId,
  onSelectEntity,
}) => {
  const [localSelectedEntityId, setLocalSelectedEntityId] = React.useState<
    string
  >(selectedEntityId || "");

  const COMPONENT_TYPE = {
    SKELETON: "Skeleton",
    NAMED_OBJECT: "NamedObject",
  };

  // Find all skeletal entities
  const skeletalEntities = React.useMemo(() => {
    const query = world.query(COMPONENT_TYPE.SKELETON);
    return query.execute();
  }, [world]);

  const selectedEntity = React.useMemo(() => {
    if (!localSelectedEntityId) return null;
    return world.getEntity(localSelectedEntityId);
  }, [world, localSelectedEntityId]);

  const handleSelectEntity = (entityId: string) => {
    setLocalSelectedEntityId(entityId);
    onSelectEntity?.(entityId);
  };

  return (
    <div className="flex h-full w-full bg-slate-950 text-slate-100">
      {/* Sidebar */}
      <aside className="hidden h-full w-64 flex-shrink-0 flex-col border-r border-slate-800 bg-slate-950/70 p-3 lg:flex">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              NEXUS · ECS
            </div>
            <div className="text-sm font-semibold text-slate-100">
              Skeleton Lab
            </div>
          </div>
          <span className="rounded-full bg-emerald-500/10 px-2 py-1 text-[10px] font-medium text-emerald-300">
            INTEGRATED
          </span>
        </div>

        {/* Entity list */}
        <div className="mb-1 text-[10px] uppercase tracking-wide text-slate-500">
          Entities · {skeletalEntities.length}
        </div>
        <div className="flex-1 space-y-1 overflow-y-auto pr-1 text-xs">
          {skeletalEntities.map((entity: any) => {
            const isActive = entity.id === localSelectedEntityId;
            const named = world.getComponent(entity.id, COMPONENT_TYPE.NAMED_OBJECT);

            return (
              <button
                key={entity.id}
                onClick={() => handleSelectEntity(entity.id)}
                className={[
                  "flex w-full items-center justify-between rounded-md px-2 py-1 text-left transition",
                  isActive
                    ? "bg-slate-800 text-slate-50 shadow-sm shadow-emerald-500/30"
                    : "text-slate-300 hover:bg-slate-900/80",
                ].join(" ")}
              >
                <span className="truncate">
                  {named?.name || entity.id}
                </span>
                <span className="text-[10px] font-semibold text-slate-500">
                  SKL
                </span>
              </button>
            );
          })}
        </div>

        {/* Entity Info */}
        {selectedEntity && (
          <div className="mt-3 space-y-1 text-[11px] text-slate-300">
            <div className="text-[10px] uppercase tracking-wide text-slate-500">
              Entity Profile
            </div>
            <div className="rounded-md border border-slate-800 bg-slate-900/70 p-2 text-[10px]">
              <div className="mb-1 font-mono text-slate-400">{selectedEntity.id}</div>
              <div className="mb-1">
                <span className="text-slate-500">Components: </span>
                <span className="text-emerald-300">
                  {selectedEntity.components.size}
                </span>
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main viewport */}
      <main className="relative flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-3 py-2 text-xs">
          <div className="flex items-center gap-2">
            <span className="rounded bg-slate-900 px-2 py-1 font-mono text-[10px] text-slate-300">
              ECS · SKELETON
            </span>
            <span className="text-slate-400">
              Entity-driven skeleton visualization
            </span>
          </div>
        </header>

        <div className="relative flex-1">
          <Canvas
            dpr={[1, 2]}
            camera={{ position: [3, 2, 4], fov: 45, near: 0.1, far: 50 }}
            gl={{ antialias: true }}
            style={{ width: "100%", height: "100%" }}
          >
            <color attach="background" args={["#020617"]} />
            <fog attach="fog" args={["#020617", 5, 18]} />

            <hemisphereLight intensity={0.75} groundColor={"#020617"} />
            <directionalLight position={[4, 6, 4]} intensity={1.2} castShadow />

            <gridHelper args={[10, 20, "#1f2937", "#020617"]} />
            <axesHelper args={[1.5]} />

            {selectedEntity && (
              <SkeletonEntityRenderer
                world={world}
                entityId={selectedEntity.id}
              />
            )}

            {/* <OrbitControls\n                enableDamping\n                dampingFactor={0.1}\n                autoRotate\n                autoRotateSpeed={2}\n              /> */}
          </Canvas>
        </div>
      </main>
    </div>
  );
};

// nexus:eof



