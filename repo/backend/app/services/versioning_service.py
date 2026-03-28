from app.utils.diffs import summarize_changes


class VersioningService:
    @staticmethod
    def build_change_summary(previous: dict | None, current: dict) -> list[dict]:
        return summarize_changes(previous, current)
