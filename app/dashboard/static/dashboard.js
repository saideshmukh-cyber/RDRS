
async function getJson(url) {
  const response = await fetch(url);

  if (response.status === 401) {
    window.location.replace("/login");
    throw new Error("Your session has expired. Please sign in again.");
  }

  if (!response.ok) {
    throw new Error(await response.text());
  }

  return response.json();
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, character => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[character]));
}

async function refresh() {
  try {
    const [status, alerts, events, incidents, health] = await Promise.all([
      getJson("/status"),
      getJson("/alerts?limit=12"),
      getJson("/events?limit=12"),
      getJson("/incidents?limit=12"),
      getJson("/health")
    ]);

    document.querySelector("#health").textContent = health.status.toUpperCase();
    document.querySelector("#level").textContent = status.level;
    document.querySelector("#score").textContent = status.score;
    document.querySelector("#window").textContent = status.window_events;
    document.querySelector("#mode").textContent =
      status.simulation_mode ? "SIMULATION" : "REVIEW CONFIG";

    document.querySelector("#alerts").innerHTML =
      alerts.map(alert => `
        <tr>
          <td>${esc(new Date(alert.timestamp).toLocaleTimeString())}</td>
          <td>${esc(alert.level)}</td>
          <td>${esc(alert.score)}</td>
          <td>${esc(alert.message)}</td>
        </tr>
      `).join("") || '<tr><td colspan="4">No alerts</td></tr>';

    document.querySelector("#events").innerHTML =
      events.map(event => `
        <tr>
          <td>${esc(event.event_type)}</td>
          <td title="${esc(event.path)}">${esc(event.path)}</td>
          <td>${event.entropy == null ? "—" : Number(event.entropy).toFixed(2)}</td>
          <td>${esc(new Date(event.timestamp).toLocaleTimeString())}</td>
        </tr>
      `).join("") || '<tr><td colspan="4">No events</td></tr>';

    document.querySelector("#incidents").innerHTML =
      incidents.map(incident => `
        <tr>
          <td>${esc(incident.id)}</td>
          <td>${esc(new Date(incident.created_at).toLocaleString())}</td>
          <td>${esc(incident.level)}</td>
          <td>${esc(incident.score)}</td>
          <td>${esc((incident.signals || []).join(", "))}</td>
        </tr>
      `).join("") || '<tr><td colspan="5">No incidents</td></tr>';

  } catch (error) {
    document.querySelector("#health").textContent = "API ERROR";
    console.error(error);
  }
}

document.querySelector("#logout-button").addEventListener("click", async () => {
  const button = document.querySelector("#logout-button");
  button.disabled = true;
  button.textContent = "Logging out…";

  try {
    const csrfResponse = await fetch("/auth/csrf");

    if (!csrfResponse.ok) {
      throw new Error("Could not obtain a security token.");
    }

    const csrfData = await csrfResponse.json();

    const response = await fetch("/auth/logout", {
      method: "POST",
      headers: {
        "X-CSRF-Token": csrfData.csrf_token
      }
    });

    if (response.status === 401) {
      window.location.replace("/login");
      return;
    }

    if (!response.ok) {
      throw new Error("Logout failed.");
    }

    window.location.replace("/login");
  } catch (error) {
    console.error(error);
    button.disabled = false;
    button.textContent = "Log out";
    alert("Unable to log out. Please try again.");
  }
});

refresh();
setInterval(refresh, 3000);
