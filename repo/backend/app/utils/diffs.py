from collections.abc import Mapping


def summarize_changes(old: dict | None, new: dict | None, prefix: str = "") -> list[dict]:
    old = old or {}
    new = new or {}
    changes: list[dict] = []
    keys = sorted(set(old.keys()) | set(new.keys()))
    for key in keys:
        path = f"{prefix}.{key}" if prefix else key
        old_value = old.get(key)
        new_value = new.get(key)
        if isinstance(old_value, Mapping) and isinstance(new_value, Mapping):
            changes.extend(summarize_changes(dict(old_value), dict(new_value), path))
            continue
        if old_value != new_value:
            changes.append({
                "field": path,
                "before": old_value,
                "after": new_value,
                "summary": f"Updated {path}",
            })
    return changes
