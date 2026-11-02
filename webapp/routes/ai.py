"""AI (Kama) routes."""

import json
import logging

from flask import Blueprint, Response, g, jsonify, request, stream_with_context

from core.security import rate_limit
from webapp.helpers import get_current_user_id

logger = logging.getLogger(__name__)

bp = Blueprint("ai", __name__)


@bp.route("/api/ask/stream", methods=["POST"])
@rate_limit(requests_per_minute=10)  # Lower limit for AI
def ask_ai_stream():
    """Stream AI responses using Server-Sent Events."""
    data = request.json or {}
    question = data.get("question", "")
    clear = data.get("clear", False)
    images = data.get("images")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get session/user for conversation isolation
    session_id = request.cookies.get("session_id")
    user_id = get_current_user_id()

    def generate():
        try:
            from core.ai import get_kama

            kama = get_kama()
            if clear:
                kama.clear_conversation(session_id, user_id)
            for event in kama.ask_stream_with_context(
                question,
                context_retriever=g.context_retriever,
                session_id=session_id,
                user_id=user_id,
                images=images,
            ):
                yield f"data: {json.dumps(event)}\n\n"
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"AI stream backend unavailable: {e}")
            yield f"data: {json.dumps({'type': 'error', 'ai_available': False, 'content': 'AI backend unavailable. Please ensure LM Studio is running or configure ANTHROPIC_API_KEY.'})}\n\n"
        except Exception as e:
            logger.error(f"AI stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@bp.route("/api/ask", methods=["POST"])
@rate_limit(requests_per_minute=10)  # Lower limit for AI
def ask_ai():
    """Ask Kama a question (non-streaming)."""
    data = request.json or {}
    question = data.get("question", "")
    clear = data.get("clear", False)
    images = data.get("images")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    try:
        # Get session/user for conversation isolation
        session_id = request.cookies.get("session_id")
        user_id = get_current_user_id()

        from core.ai import ask_kama

        response = ask_kama(
            question,
            clear=clear,
            session_id=session_id,
            user_id=user_id,
            images=images,
        )
        return jsonify({"response": response})

    except (ConnectionError, TimeoutError) as e:
        logger.warning(f"AI backend unavailable: {e}")
        return (
            jsonify(
                {
                    "ai_available": False,
                    "error": "AI backend unavailable",
                    "message": "The AI assistant is currently offline. Please ensure Ollama is running or configure a cloud AI provider (ANTHROPIC_API_KEY).",
                    "help": "For LM Studio: open LM Studio and start a local server on port 1234. For Ollama: run 'ollama serve'. For cloud: set ANTHROPIC_API_KEY.",
                }
            ),
            503,
        )
    except Exception as e:
        logger.error(f"AI error: {e}")
        return jsonify({"error": str(e)}), 500
