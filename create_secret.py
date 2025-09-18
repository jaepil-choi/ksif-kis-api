"""
---
Purpose: Generate one or more KIS secret files from environment variables.
Contents:
    - Load .env
    - Validate required variables (no silent None)
    - Support multiple REAL accounts (REAL1_*, REAL2_*, ...) -> secret{n}.json
    - Backward-compatible single set (REAL_*) -> secret.json
---
"""

from pathlib import Path
import logging
import os
import re
from typing import Dict, Iterable, List, Optional

from dotenv import load_dotenv
from pykis import KisAuth


def _setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _find_account_indices(env_keys: Iterable[str]) -> List[str]:
    """
    Find indices N for which any REALN_* variables exist.
    Returns indices as strings sorted by numeric value (e.g., ["1", "2"]).
    """
    indices = set()
    for key in env_keys:
        for suffix in ("APP_KEY", "APP_SECRET", "ACC_NO"):
            m = re.match(rf"^REAL(\d+)_({suffix})$", key)
            if m:
                indices.add(m.group(1))
                break
    return sorted(indices, key=lambda s: int(s))


def collect_accounts_from_env() -> List[Dict[str, Optional[str]]]:
    """
    Collect account credentials from environment without validation.
    Returns a list of dicts with keys: index (str|None), appkey, secretkey, account.
    """
    indices = _find_account_indices(os.environ.keys())
    accounts: List[Dict[str, Optional[str]]] = []

    if indices:
        for idx in indices:
            accounts.append(
                {
                    "index": idx,
                    "appkey": os.getenv(f"REAL{idx}_APP_KEY"),
                    "secretkey": os.getenv(f"REAL{idx}_APP_SECRET"),
                    "account": os.getenv(f"REAL{idx}_ACC_NO"),
                }
            )
        return accounts

    # Legacy single account (unnumbered)
    accounts.append(
        {
            "index": None,
            "appkey": os.getenv("REAL_APP_KEY"),
            "secretkey": os.getenv("REAL_APP_SECRET"),
            "account": os.getenv("REAL_ACC_NO"),
        }
    )
    return accounts


def validate_env(hts_id: Optional[str], accounts: List[Dict[str, Optional[str]]]) -> None:
    """Validate required environment variables; raise RuntimeError on issues."""
    if not hts_id:
        raise RuntimeError("Missing required environment variable: HTS_ID")

    # Numbered vs legacy mode
    numbered = all(acc["index"] is not None for acc in accounts)
    if numbered:
        missing_by_index: List[str] = []
        for acc in accounts:
            idx = str(acc["index"])  # not None here
            required = {
                f"REAL{idx}_APP_KEY": acc.get("appkey"),
                f"REAL{idx}_APP_SECRET": acc.get("secretkey"),
                f"REAL{idx}_ACC_NO": acc.get("account"),
            }
            missing = [name for name, val in required.items() if not val]
            if missing:
                missing_by_index.append(f"[{idx}] missing: {', '.join(missing)}")
        if missing_by_index:
            details = "\n".join(missing_by_index)
            raise RuntimeError(
                "Missing required environment variables for some REAL accounts:\n" + details
            )
        return

    # Legacy single account
    legacy_required = {
        "REAL_APP_KEY": accounts[0].get("appkey"),
        "REAL_APP_SECRET": accounts[0].get("secretkey"),
        "REAL_ACC_NO": accounts[0].get("account"),
    }
    missing_legacy = [name for name, val in legacy_required.items() if not val]
    if missing_legacy:
        raise RuntimeError(
            "No numbered REAL account variables found. "
            "Legacy variables are also incomplete. Missing: "
            + ", ".join(missing_legacy)
        )


def save_secrets(hts_id: str, accounts: List[Dict[str, Optional[str]]]) -> None:
    """Create KisAuth for each account and save to appropriate file."""
    for acc in accounts:
        appkey = str(acc["appkey"])  # safe after validate_env
        secretkey = str(acc["secretkey"])  # safe after validate_env
        account = str(acc["account"])  # safe after validate_env

        auth = KisAuth(
            id=hts_id,
            appkey=appkey,
            secretkey=secretkey,
            account=account,
            virtual=False,
        )

        idx = acc["index"]
        out_path = Path(f"secret{idx}.json") if idx is not None else Path("secret.json")
        auth.save(str(out_path))
        logging.info("Saved %s", out_path)


def main() -> None:
    # Load environment variables and configure logging
    load_dotenv()
    _setup_logging()

    hts_id = os.getenv("HTS_ID")
    accounts = collect_accounts_from_env()
    validate_env(hts_id, accounts)
    save_secrets(str(hts_id), accounts)
    logging.info("Created %s secret file(s).", len(accounts))


if __name__ == "__main__":
    main()