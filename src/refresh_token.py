"""Weekly job: extend the Instagram Login token (valid 60 days) and store it back as the repo secret.
Needs the GH_PAT secret (fine-grained token, this repo only, permission "Secrets: Read and write").
Without GH_PAT it only checks the token and warns on Telegram well before it expires."""
import base64, os, sys, traceback
import requests

from .instagram import refresh_token
from .telegram import Telegram


def store_secret(name, value):
    repo = os.environ["GITHUB_REPOSITORY"]; pat = os.environ["GH_PAT"]
    h = {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    k = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=h, timeout=30)
    k.raise_for_status(); k = k.json()
    from nacl import encoding, public
    box = public.SealedBox(public.PublicKey(k["key"].encode(), encoding.Base64Encoder()))
    enc = base64.b64encode(box.encrypt(value.encode())).decode()
    r = requests.put(f"https://api.github.com/repos/{repo}/actions/secrets/{name}", headers=h, timeout=30,
                     json={"encrypted_value": enc, "key_id": k["key_id"]})
    r.raise_for_status()


def main():
    if os.environ.get("IG_LOGIN", "instagram") == "facebook":
        print("Facebook Login page tokens do not expire; nothing to do."); return
    tg = Telegram()
    new, expires_in = refresh_token(os.environ["IG_ACCESS_TOKEN"])
    days = expires_in // 86400
    if new != os.environ["IG_ACCESS_TOKEN"]:
        if os.environ.get("GH_PAT"):
            store_secret("IG_ACCESS_TOKEN", new)
            print(f"token refreshed and stored, valid {days} days")
        else:
            tg.send_message("⚠️ Instagram token'ı yenilendi ama GH_PAT secret'ı olmadığı için kaydedilemedi. "
                            f"Eski token yaklaşık {days} gün içinde geçersiz olabilir; README'deki GH_PAT adımını yap.")
    else:
        print(f"token extended in place, valid {days} days")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        try:
            Telegram().send_message(f"❌ Instagram token'ı yenilenemedi: {e}\nToken'ın süresi dolmadan yenisini üretip IG_ACCESS_TOKEN secret'ına koy.")
        except Exception:
            pass
        sys.exit(1)
