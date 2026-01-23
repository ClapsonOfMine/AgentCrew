"""Conversation browser input handling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

from loguru import logger

if TYPE_CHECKING:
    from .browser_ui import ConversationBrowserUI


class ConversationBrowserInputHandler:
    """Handles keyboard input for the conversation browser."""

    def __init__(
        self,
        ui: ConversationBrowserUI,
        on_select: Optional[Callable[[str], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        self._ui = ui
        self._running = False
        self._g_pressed = False
        self._selected_id: Optional[str] = None
        self._on_select = on_select
        self._on_cancel = on_cancel

    def _create_key_bindings(self) -> KeyBindings:
        """Create and configure key bindings for the browser."""
        kb = KeyBindings()

        @kb.add(Keys.Up)
        @kb.add("k")
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("up"):
                self._ui.render()

        @kb.add(Keys.Down)
        @kb.add("j")
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("down"):
                self._ui.render()

        @kb.add(Keys.ControlP)
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("up"):
                self._ui.render()

        @kb.add(Keys.ControlN)
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("down"):
                self._ui.render()

        @kb.add("g")
        def _(event):
            if self._g_pressed:
                self._g_pressed = False
                if self._ui.handle_navigation("top"):
                    self._ui.render()
            else:
                self._g_pressed = True

        @kb.add("G")
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("bottom"):
                self._ui.render()

        @kb.add(Keys.ControlU)
        @kb.add(Keys.PageUp)
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("page_up"):
                self._ui.render()

        @kb.add(Keys.ControlD)
        @kb.add(Keys.PageDown)
        def _(event):
            self._g_pressed = False
            if self._ui.handle_navigation("page_down"):
                self._ui.render()

        @kb.add(Keys.Enter)
        @kb.add("l")
        def _(event):
            self._g_pressed = False
            self._selected_id = self._ui.get_selected_conversation_id()
            event.app.exit()

        @kb.add(Keys.Escape)
        @kb.add("q")
        def _(event):
            self._g_pressed = False
            event.app.exit()

        @kb.add(Keys.ControlC)
        def _(event):
            self._g_pressed = False
            event.app.exit()

        @kb.add(Keys.Any)
        def _(event):
            self._g_pressed = False

        return kb

    def run(self) -> Optional[str]:
        """Run the input handler loop.

        Returns:
            The ID of the selected conversation, or None if cancelled.
        """
        self._running = True
        self._g_pressed = False
        self._selected_id = None

        self._ui.render()

        kb = self._create_key_bindings()

        try:
            session = PromptSession(key_bindings=kb)
            session.prompt("")
        except (KeyboardInterrupt, EOFError):
            pass
        except Exception as e:
            logger.error(f"Error in conversation browser input handler: {e}")

        self._running = False
        return self._selected_id

    @property
    def is_running(self) -> bool:
        """Check if the input handler is currently running."""
        return self._running

    def stop(self):
        """Stop the input handler."""
        self._running = False
