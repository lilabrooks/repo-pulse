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

// Extract owner/repo from bare "owner/repo", "github.com/owner/repo", or a full
// https://github.com/owner/repo[/...] URL. Returns {owner, repo} or {error}.
// Non-GitHub hosts are rejected rather than silently mis-parsed; owner/repo come
// from the GitHub REST API only (docs/specs/frontend.md).
function parseRepo(raw) {
  let value = raw.trim()
    .replace(/^https?:\/\//i, "")
    .replace(/^www\./i, "")
    .split(/[?#]/)[0];

  const gh = value.match(/^github\.com\/(.+)$/i);
  if (gh) {
    value = gh[1];
  } else if (/^[^/\s]+\.[^/\s]+\//.test(value)) {
    return { error: "That looks like a non-GitHub URL. Enter owner/repo or a github.com URL." };
  }

  const parts = value.split("/").filter(Boolean);
  if (parts.length < 2) {
    return { error: "Enter a repository as owner/repo." };
  }
  const owner = parts[0];
  const repo = parts[1].replace(/\.git$/i, "");
  if (!owner || !repo) {
    return { error: "Enter a repository as owner/repo." };
  }
  return { owner, repo };
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
  const parsed = parseRepo(input.value);
  if (parsed.error) {
    setStatus(parsed.error, "error");
    return;
  }
  const slug = parsed.owner + "/" + parsed.repo;

  dashboard.hidden = true;
  setStatus("Checking pulse of " + slug + " …", "loading");

  try {
    const response = await fetch(
      "/api/repo/" + encodeURIComponent(parsed.owner) + "/" + encodeURIComponent(parsed.repo)
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
