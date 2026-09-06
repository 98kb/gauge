// Token expiry is checked on every request at the authentication boundary.
const DEFAULT_TTL_SECONDS = 3600;

export function isExpired(token, now = Date.now()) {
  return now >= token.issuedAt + DEFAULT_TTL_SECONDS * 1000;
}

export function refresh(token) {
  return { ...token, issuedAt: Date.now() };
}
