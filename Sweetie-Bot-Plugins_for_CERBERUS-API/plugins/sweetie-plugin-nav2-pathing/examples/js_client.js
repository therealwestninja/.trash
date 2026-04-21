const payload = {
  type: "nav.goal",
  payload: { x: 2.25, y: 0.75, yaw: 0.0, frame: "map" }
};

fetch("http://localhost:7000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
})
  .then((r) => r.json())
  .then((data) => console.log(data))
  .catch((err) => console.error(err));
