export function settle(entries) {
  return entries.filter((entry) => entry.state === "open");
}
