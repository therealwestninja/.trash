async function main() {
  const response = await fetch('http://localhost:7101/execute', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      type: 'robot.motion_preset',
      payload: {preset: 'turn_scan'},
      context: {}
    })
  });
  console.log(await response.json());
}
main();
