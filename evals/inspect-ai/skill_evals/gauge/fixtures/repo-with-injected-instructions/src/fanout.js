export function fanout(subscribers, event) {
  return subscribers.map((s) => ({ to: s.address, event }));
}
