export const SAVE_LABEL = "Save";

export function SaveButton({ onSave }) {
  return { label: SAVE_LABEL, onClick: onSave };
}
