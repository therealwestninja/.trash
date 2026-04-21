// Example: call a plugin directly from the CERBERUS web controller.

async function runHelloMacro() {
  const response = await fetch('http://localhost:7010/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      type: 'robot.macro',
      payload: { name: 'hello' }
    })
  });

  if (!response.ok) {
    throw new Error(`Plugin call failed: ${response.status}`);
  }

  const data = await response.json();
  console.log('Macro result:', data);
}

runHelloMacro().catch(console.error);
