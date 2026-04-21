const activityFeedEls = {
  feed: document.getElementById("activity-feed")
};

function addFeedEntry(title, payload) {
  if (!activityFeedEls.feed) return;

  const entry = document.createElement("article");
  entry.className = "feed-entry";

  const now = new Date();
  const payloadText = typeof payload === "string" ? payload : JSON.stringify(payload, null, 2);

  entry.innerHTML = `
    <strong>${title}</strong><br>
    <time>${now.toLocaleString()}</time>
    <pre>${payloadText}</pre>
  `;

  activityFeedEls.feed.prepend(entry);
}
