"""Temporary public URL for a video: a one-commit orphan branch `media` on this (public) repo,
served by raw.githubusercontent.com. Force-pushed each time, so it never grows the history,
and deleted again after Instagram has fetched the video."""
import os, subprocess, tempfile

BRANCH = "media"


def _remote():
    repo = os.environ["GITHUB_REPOSITORY"]          # set by GitHub Actions
    tok = os.environ["GITHUB_TOKEN"]
    return repo, f"https://x-access-token:{tok}@github.com/{repo}.git"


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def publish(video_bytes, name):
    repo, remote = _remote()
    with tempfile.TemporaryDirectory() as d:
        _git(d, "init", "-q", "-b", BRANCH)
        with open(os.path.join(d, name), "wb") as f:
            f.write(video_bytes)
        _git(d, "add", name)
        _git(d, "-c", "user.name=hergunyenibirbilgi-bot", "-c", "user.email=actions@users.noreply.github.com",
             "commit", "-q", "-m", "temporary video for Instagram")
        _git(d, "push", "-q", "-f", remote, f"{BRANCH}:{BRANCH}")
    return f"https://raw.githubusercontent.com/{repo}/{BRANCH}/{name}"


def cleanup():
    try:
        repo, remote = _remote()
        subprocess.run(["git", "push", "-q", remote, "--delete", BRANCH], check=False, capture_output=True)
    except Exception:
        pass
