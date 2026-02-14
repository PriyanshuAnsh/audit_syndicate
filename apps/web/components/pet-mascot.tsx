type PetMascotProps = {
  stage?: "egg" | "baby" | "teen" | "adult" | string;
  name?: string;
  level?: number;
  compact?: boolean;
};

export default function PetMascot({ stage = "baby", name = "Sprout", level = 1, compact = false }: PetMascotProps) {
  const stageClass = `pet-stage-${stage}`;

  return (
    <div className={`pet-scene ${compact ? "pet-scene-compact" : ""}`}>
      <div className="pet-aura" />
      <div className={`pet-wrap ${stageClass}`}>
        <div className="pet-ear pet-ear-left" />
        <div className="pet-ear pet-ear-right" />
        <div className="pet-body">
          <div className="pet-eye pet-eye-left"><span /></div>
          <div className="pet-eye pet-eye-right"><span /></div>
          <div className="pet-mouth" />
          <div className="pet-cheek pet-cheek-left" />
          <div className="pet-cheek pet-cheek-right" />
          <div className="pet-belly" />
        </div>
        <div className="pet-tail" />
        <div className="pet-shadow" />
      </div>
      <div className="pet-card glass">
        <p className="pet-name">{name}</p>
        <p className="pet-meta">Level {level} • {stage}</p>
      </div>
    </div>
  );
}
