from app.utils.diffs import summarize_changes


def test_version_diff_summary_tracks_field_changes():
    diff = summarize_changes({"a": 1, "nested": {"b": 2}}, {"a": 3, "nested": {"b": 4}})
    fields = {item["field"] for item in diff}
    assert "a" in fields
    assert "nested.b" in fields
