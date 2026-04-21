fetch("http://localhost:7000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    type: "world.query_near",
    payload: {
      origin: { x: 0.0, y: 0.0, z: 0.0 },
      radius_m: 5.0,
      labels: ["person", "charging_dock"]
    }
  })
})
  .then((r) => r.json())
  .then((data) => console.log(data))
  .catch((err) => console.error(err));
