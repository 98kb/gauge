export function render(rows) {
  return rows.map((row) => row.join(","));
}
