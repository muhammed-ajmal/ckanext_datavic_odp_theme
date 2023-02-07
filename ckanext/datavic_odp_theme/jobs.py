from __future__ import annotations

import os
import logging
from typing import Optional

import requests

from ckan import model
from ckan.lib.search import rebuild, commit


log = logging.getLogger(__name__)


def reindex_organization(id_or_name: str):
    """Rebuild search index for all datasets inside the organization."""
    org = model.Group.get(id_or_name)
    if not org:
        log.warning("Organization with ID or name %s not found", id_or_name)
        return

    query = model.Session.query(model.Package.id).filter_by(owner_org=org.id)

    rebuild(package_ids=(p.id for p in query), force=True)
    commit()


def ckan_worker_job_monitor() -> None:
    monitor_url: Optional[str] = os.environ.get("MONITOR_URL_JOBWORKER")

    if not monitor_url:
        return log.error(
            "The env variable MONITOR_URL_JOBWORKER is not set for CKAN worker job monitor"
        )

    try:
        log.info("Sending notification for CKAN worker job monitor")
        requests.get(monitor_url, timeout=10)
    except requests.RequestException as e:
        log.error(
            "Failed to send CKAN worker job monitor notification to %s", monitor_url
        )
        log.error(str(e))

    log.info("Successfully sent notification for CKAN worker job monitor")
