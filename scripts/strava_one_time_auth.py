"""
Strava 一次性授權腳本 — 在 Zoe 的電腦上執行一次，取得永久 refresh token。

使用方式：
    python scripts/strava_one_time_auth.py

需要準備：
    - Strava Developer App 的 Client ID 和 Client Secret
    - 去 developers.strava.com/settings 建立 App，
      Authorization Callback Domain 填 "localhost"
"""
import webbrowser, requests, sys
from urllib.parse import urlparse, parse_qs


def main():
    print("=" * 55)
    print("  HYROX War Room — Strava 一次性授權")
    print("=" * 55)
    print()

    client_id = input("1. 請輸入 Strava Client ID：").strip()
    client_secret = input("2. 請輸入 Strava Client Secret：").strip()

    auth_url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}"
        "&redirect_uri=http://localhost/"
        "&response_type=code"
        "&approval_prompt=auto"
        "&scope=activity:read_all"
    )

    print()
    print("3. 即將開啟瀏覽器，請用 Zoe 的 Strava 帳號授權...")
    print("   授權後瀏覽器會跳到「找不到網頁」的頁面，這是正常的。")
    input("   按 Enter 開啟瀏覽器...")
    webbrowser.open(auth_url)

    print()
    print("4. 從瀏覽器網址列複製完整 URL（以 http://localhost/?code= 開頭）")
    callback_url = input("   貼上 URL：").strip()

    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]
    if not code:
        print("\n❌ 找不到授權碼，請確認 URL 是否正確。")
        sys.exit(1)

    print("\n5. 正在交換 access token...")
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id":     client_id,
        "client_secret": client_secret,
        "code":          code,
        "grant_type":    "authorization_code",
    }, timeout=10)

    if not r.ok:
        print(f"\n❌ 失敗：{r.text}")
        sys.exit(1)

    token = r.json()
    athlete = token.get("athlete", {})
    print(f"\n✓ 授權成功！")
    print(f"   運動員：{athlete.get('firstname')} {athlete.get('lastname')} (ID: {athlete.get('id')})")
    print()
    print("=" * 55)
    print("  請把以下 4 個值加進 GitHub Secrets：")
    print("  github.com/Randall2000/coros → Settings →")
    print("  Secrets and variables → Actions")
    print("=" * 55)
    print(f"  STRAVA_CLIENT_ID     = {client_id}")
    print(f"  STRAVA_CLIENT_SECRET = {client_secret}")
    print(f"  STRAVA_REFRESH_TOKEN = {token.get('refresh_token')}")
    print(f"  STRAVA_ATHLETE_ID    = {athlete.get('id')}")
    print("=" * 55)
    print()
    print("完成後，在 GitHub Actions 手動觸發 'Sync Strava (Zoe)' workflow。")


if __name__ == "__main__":
    main()
