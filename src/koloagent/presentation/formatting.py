def render_devin_turn(buffer: str, session_url: str) -> str:
    return f"**🤖 Devin**\n\n{buffer}\n\n---\n\n[открыть сессию]({session_url})"
