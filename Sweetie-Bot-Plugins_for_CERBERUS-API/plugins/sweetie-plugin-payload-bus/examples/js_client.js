fetch("http://localhost:7000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    type: "payload.list_by_capability",
    payload: { capability: "vision.detect" }
  })
})
  .then((r) => r.json())
  .then((data) => console.log(data))
  .catch((err) => console.error(err));
