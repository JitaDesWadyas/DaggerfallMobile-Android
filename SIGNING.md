# Updating without uninstalling

Android requires all three to update an installed app:
1. Identical package name (`dev.daggerfall.mobile`).
2. Increasing `versionCode`.
3. APKs signed with the **same private key/certificate**.

The older GitHub Actions debug builds used a disposable per-run debug signing key. They **cannot update one another reliably**. A one-time migration from a differently signed debug build may be necessary.

## One-time signing setup

Open GitHub repository **Settings → Secrets and variables → Actions → New repository secret**.

Name: `APK_SIGNING_KEY_B64`

Value: the contents of the privately held `DaggerfallMobile_APK_SIGNING_KEY_B64.txt` supplied to the project owner. **Never commit, paste into an issue, or publish this value**.

The public matching certificate is stored at `signing/public-cert.pem` (safe to publish).

After saving the secret, run **Actions → Build Android APK → Run workflow**.
A successful run creates an artifact `DaggerfallMobile-release-apk`, containing a release-signed APK. Every subsequent release build uses the same key, with an increasing versionCode, so it installs over the previous release build without uninstalling.

Until that secret is configured, the workflow produces a clearly labeled **test-only debug APK**, which is *not* guaranteed to update in place.

Do not lose the secret key. Losing it prevents updates to installed apps using that signature. Keep a secure private backup.
