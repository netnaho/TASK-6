from datetime import datetime


def render_plan_pdf(plan_title: str, participant_name: str, summary: str) -> bytes:
    content = (
        "NutriDeclare Final Plan\n"
        f"Participant: {participant_name}\n"
        f"Plan: {plan_title}\n"
        f"Generated: {datetime.utcnow().isoformat()}Z\n\n"
        f"Summary:\n{summary}\n"
    )
    return content.encode()
