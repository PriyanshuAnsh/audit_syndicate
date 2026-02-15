type PetMascotProps = {
  stage?: "egg" | "baby" | "teen" | "adult" | string;
  name?: string;
  level?: number;
  compact?: boolean;
  equippedItems?: Array<{
    item_id: number;
    name: string;
    slot: string;
    type: string;
    metadata_json?: {
      image_url?: string;
      pet_asset?: string;
      pet_style?: string;
      pet_layer?: string;
    };
  }>;
};

export default function PetMascot({
  stage = "baby",
  name = "Sprout",
  level = 1,
  compact = false,
  equippedItems = [],
}: PetMascotProps) {
  const stageClass = `pet-stage-${stage}`;
  const isEgg = stage === "egg";
  // Equipped item rendering is currently disabled.
  // const bySlot = Object.fromEntries(equippedItems.map((item) => [item.slot, item]));
  // const skinClass = bySlot.skin?.metadata_json?.pet_style ? `pet-skin-${bySlot.skin.metadata_json.pet_style}` : "";
  // const habitatClass = bySlot.background?.metadata_json?.pet_style ? `pet-habitat-${bySlot.background.metadata_json.pet_style}` : "";
  void equippedItems;
  const skinClass = "";
  const habitatClass = "";

  return (
    <div className={`pet-scene ${habitatClass} ${compact ? "pet-scene-compact" : ""}`}>
      <div className="pet-aura" />
      <div className={`pet-wrap ${stageClass}`}>
        {/* Equipped overlays disabled */}
        <div className="pet-ear pet-ear-left" />
        <div className="pet-ear pet-ear-right" />
        <div className={`pet-body ${skinClass}`}>
          {isEgg ? (
            <>
              <div className="pet-egg-speck pet-egg-speck-1" />
              <div className="pet-egg-speck pet-egg-speck-2" />
              <div className="pet-egg-speck pet-egg-speck-3" />
              <div className="pet-egg-crack" />
            </>
          ) : (
            <>
              <div className="pet-eye pet-eye-left"><span /></div>
              <div className="pet-eye pet-eye-right"><span /></div>
              <div className="pet-mouth" />
              <div className="pet-cheek pet-cheek-left" />
              <div className="pet-cheek pet-cheek-right" />
              <div className="pet-belly" />
            </>
          )}
        </div>
        {/* Equipped overlays disabled */}
        <div className="pet-tail" />
        <div className="pet-shadow" />
      </div>
    </div>
  );
}
