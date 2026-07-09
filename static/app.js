/* Repo Pulse dashboard: consumes GET /api/repo/{owner}/{repo} per docs/specs/api.md. */

const form = document.getElementById("repo-form");
const input = document.getElementById("repo-input");
const status = document.getElementById("status");
const dashboard = document.getElementById("dashboard");

function setStatus(message, kind) {
  status.textContent = message || "";
  status.hidden = !message;
  status.className = kind || "";
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function render(data) {
  const banner = document.getElementById("pulse-banner");
  banner.textContent = data.pulse.verdict.toUpperCase() + " — " + data.pulse.reasons.join("; ");
  banner.className = "banner " + data.pulse.verdict;

  setText("repo-name", data.repo.full_name);
  setText("repo-description", data.repo.description || "");
  setText("stat-stars", data.repo.stars.toLocaleString());
  setText("stat-forks", data.repo.forks.toLocaleString());
  setText("stat-watchers", data.repo.watchers.toLocaleString());
  setText("stat-issues", data.issues.open_issues.toLocaleString());
  setText("stat-prs", data.issues.open_prs.toLocaleString());
  setText("stat-commits", data.activity.commits_last_30d.toLocaleString());
  setText("stat-release", data.release
    ? data.release.tag + " (" + (data.release.published_at || "").slice(0, 10) + ")"
    : "none");
  setText("stat-license", data.repo.license || "none detected");
  document.getElementById("repo-link").href = data.repo.html_url;

  dashboard.hidden = false;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const value = input.value.trim();
  const parts = value.split("/");
  if (parts.length !== 2 || !parts[0] || !parts[1]) {
    setStatus("Enter a repository as owner/repo.", "error");
    return;
  }

  dashboard.hidden = true;
  setStatus("Checking pulse of " + value + " …", "loading");

  try {
    const response = await fetch(
      "/api/repo/" + encodeURIComponent(parts[0]) + "/" + encodeURIComponent(parts[1])
    );
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      setStatus(body.detail || ("Request failed (" + response.status + ")"), "error");
      return;
    }
    render(await response.json());
    setStatus("");
  } catch (err) {
    setStatus("Could not reach the Repo Pulse backend. Is `make run` running?", "error");
  }
});
