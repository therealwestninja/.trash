fetch("http://localhost:7000/execute", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    type: "action.list",
    payload: {}
  })
})
  .then((r) => r.json())
  .then((data) => console.log(data))
  .catch((err) => console.error(err));
