
export async function sendNudge(intent) {
  return fetch("/character/nudge", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ intent })
  }).then(r => r.json());
}
