"""SaigonTech theme styles for AgentCrew GUI - Dark theme with brand green accents."""


class SaigonTechTheme:
    """Static class containing SaigonTech theme styles."""

    # Main application styles
    MAIN_STYLE = """
QMainWindow {
    background-color: #0f172a; /* Primary Background - Slate 900 */
}
QScrollArea {
    border: none;
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
QWidget#chatContainer { /* Specific ID for chat_container */
    background-color: #0f172a; /* Primary Background - Slate 900 */
}
QSplitter::handle {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
QSplitter::handle:hover {
    background-color: #475569; /* Borders - Slate 600 */
}
QSplitter::handle:pressed {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
}
QStatusBar {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QToolTip {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 4px;
}
QMessageBox {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
QMessageBox QLabel { /* For message text in QMessageBox */
    color: #f8fafc; /* Primary Text - Slate 50 */
    background-color: transparent; /* Ensure no overriding background */
}
/* QCompleter's popup is often a QListView */
QListView { /* General style for QListView, affects completer */
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 2px;
    outline: 0px; /* Remove focus outline if not desired */
}
QListView::item {
    padding: 4px 8px;
    border-radius: 2px; /* Optional: rounded corners for items */
}
QListView::item:selected {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QListView::item:hover {
    background-color: #475569; /* Borders - Slate 600 */
}

/* Modern Scrollbar Styles */
QScrollBar:vertical {
    border: none;
    background: #1e293b; /* Card/Container Background - Slate 800 */
    width: 10px; /* Adjust width for a thinner scrollbar */
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #475569; /* Borders - Slate 600 */
    min-height: 20px; /* Minimum handle size */
    border-radius: 5px; /* Rounded corners for the handle */
}
QScrollBar::handle:vertical:hover {
    background: #64748b; /* Accent/Hover - Slate 500 */
}
QScrollBar::handle:vertical:pressed {
    background: #7fb239; /* Primary Green */
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none; /* Hide arrow buttons */
    height: 0px;
    subcontrol-position: top;
    subcontrol-origin: margin;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none; /* Track area above/below handle */
}

QScrollBar:horizontal {
    border: none;
    background: #1e293b; /* Card/Container Background - Slate 800 */
    height: 10px; /* Adjust height for a thinner scrollbar */
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:horizontal {
    background: #475569; /* Borders - Slate 600 */
    min-width: 20px; /* Minimum handle size */
    border-radius: 5px; /* Rounded corners for the handle */
}
QScrollBar::handle:horizontal:hover {
    background: #64748b; /* Accent/Hover - Slate 500 */
}
QScrollBar::handle:horizontal:pressed {
    background: #7fb239; /* Primary Green */
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none; /* Hide arrow buttons */
    width: 0px;
    subcontrol-position: left;
    subcontrol-origin: margin;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none; /* Track area left/right of handle */
}

/* Context menu styling for QLabel widgets */
QLabel QMenu {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 4px;
    border-radius: 6px;
}
QLabel QMenu::item {
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    margin: 2px;
}
QLabel QMenu::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QLabel QMenu::item:pressed {
    background-color: #638b2c; /* Secondary Green */
    color: #ffffff; /* Green on White Text */
}
QLabel QMenu::separator {
    height: 1px;
    background: #475569; /* Borders - Slate 600 */
    margin: 4px 8px;
}
"""

    # Button styles
    PRIMARY_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 4px; 
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    SECONDARY_BUTTON = """
QPushButton {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: none;
    border-radius: 4px; 
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
    color: #ffffff; /* Green on White Text */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    STOP_BUTTON = """
QPushButton {
    background-color: #ef4444; /* Destructive/Error - Red 500 */
    color: #ffffff; /* White */
    border: none;
    border-radius: 4px; 
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #dc2626; /* Darker red for hover */
}
QPushButton:pressed {
    background-color: #b91c1c; /* Even darker red for pressed */
}
"""

    RED_BUTTON = """
QPushButton {
    background-color: #ef4444; /* Destructive/Error - Red 500 */
    color: #ffffff; /* White */
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #dc2626; /* Darker red for hover */
}
QPushButton:pressed {
    background-color: #b91c1c; /* Even darker red for pressed */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    GREEN_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    API_KEYS_GROUP = """
QGroupBox {
    background-color: #0f172a; /* Primary Background - Slate 900 */
}
QLabel {
    background-color: #0f172a; /* Primary Background - Slate 900 */
}
"""

    EDITOR_CONTAINER_WIDGET = """
QWidget {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
"""

    MENU_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
    padding-left: 12px; /* Add some padding for text */
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
QPushButton::menu-indicator {
    /* image: url(myindicator.png); Adjust if using a custom image */
    subcontrol-origin: padding;
    subcontrol-position: right center;
    right: 5px; /* Adjust as needed to position from the right edge */
    width: 16px; /* Ensure there's enough space for the indicator */
}
"""

    DISABLED_BUTTON = """
QPushButton {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
    border: none;
    border-radius: 4px; 
    padding: 8px;
    font-weight: bold;
}
"""

    STOP_BUTTON_STOPPING = """
QPushButton {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
    border: none;
    border-radius: 4px; 
    padding: 8px;
    font-weight: bold;
}
"""

    COMBO_BOX = """
QComboBox {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 6px 8px;
    min-width: 120px;
}
QComboBox:hover {
    border: 1px solid #64748b; /* Accent/Hover - Slate 500 */
}
QComboBox:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 1px;
    border-left-color: #475569; /* Borders - Slate 600 */
    border-left-style: solid;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: #475569; /* Borders - Slate 600 */
}
QComboBox::down-arrow {
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #f8fafc; /* Primary Text - Slate 50 */
}
QComboBox QAbstractItemView {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    selection-background-color: #7fb239; /* Primary Green */
    selection-color: #ffffff; /* Green on White Text */
    outline: 0px;
}
"""

    # Input styles
    TEXT_INPUT = """
QTextEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
}
QTextEdit:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
"""

    LINE_EDIT = """
QLineEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
}
QLineEdit:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
"""

    # Menu styles
    MENU_BAR = """
QMenuBar {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 2px;
}
QMenuBar::item {
    background-color: transparent;
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 4px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected { /* When menu is open or item is hovered */
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
QMenuBar::item:pressed { /* When menu item is pressed to open the menu */
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QMenu {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px; /* Add border-radius to menu items */
}
QMenu::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QMenu::separator {
    height: 1px;
    background: #475569; /* Borders - Slate 600 */
    margin-left: 10px;
    margin-right: 5px;
}
"""

    CONTEXT_MENU = """
QMenu {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 4px;
    border-radius: 6px;
}
QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    margin: 2px;
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QMenu::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QMenu::item:pressed {
    background-color: #638b2c; /* Secondary Green */
    color: #ffffff; /* Green on White Text */
}
QMenu::item:disabled {
    background-color: transparent;
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
QMenu::separator {
    height: 1px;
    background: #475569; /* Borders - Slate 600 */
    margin: 4px 8px;
}
"""

    AGENT_MENU = """
QMenu {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    background-color: transparent;
}
QMenu::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border-radius: 3px;
}
QMenu::separator {
    height: 1px;
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    margin-left: 5px;
    margin-right: 5px;
}
"""

    # Label styles
    STATUS_INDICATOR = """
QLabel {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 8px; 
    border-radius: 5px;
    font-weight: bold;
}
"""

    VERSION_LABEL = """
QLabel {
    color: #94a3b8; /* Secondary Text - Slate 400 */
    padding: 2px 8px;
    font-size: 11px;
}
"""

    SYSTEM_MESSAGE_TOGGLE_BUTTON = """
QPushButton {
    background-color: transparent;
    color: #7fb239; /* Primary Green */
    border: none;
    text-align: left;
    padding: 2px;
}
QPushButton:hover {
    color: #638b2c; /* Secondary Green */
}
"""

    # Widget-specific styles
    SIDEBAR = """
background-color: #1e293b; /* Sidebar Background - Slate 800 */
"""

    CONVERSATION_LIST = """
QListWidget {
    background-color: #0f172a; /* Primary Background - Slate 900 */
    border: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
    border-radius: 4px;
}
QListWidget::item {
    color: #f8fafc; /* Primary Text - Slate 50 */
    background-color: #0f172a; /* Primary Background - Slate 900 */
    border: none; /* Remove individual item borders if not desired */
    border-bottom: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
    margin: 0px; /* Remove margin if using border for separation */
    padding: 8px;
}
QListWidget::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QListWidget::item:hover:!selected {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
"""

    SEARCH_BOX = """
QLineEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
}
QLineEdit:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
"""

    TOKEN_USAGE = """
QLabel {
    color: #f8fafc; /* Primary Text - Slate 50 */
    font-weight: bold;
    padding: 8px;
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    border-top: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
}
"""

    TOKEN_USAGE_WIDGET = """
background-color: #1e293b; /* Card/Container Background - Slate 800 */
"""

    # Message bubble styles
    USER_BUBBLE = """
QFrame { 
    border-radius: 5px; 
    background-color: #7fb239; /* User Message Background - Primary Green */
    border: none;
    padding: 2px;
}
"""

    ASSISTANT_BUBBLE = """
QFrame { 
    border-radius: 5px; 
    background-color: #334155; /* Assistant Message Background - Slate 700 */
    border: none;
    padding: 2px;
}
"""

    THINKING_BUBBLE = """
QFrame { 
    border-radius: 5px; 
    background-color: #475569; /* Borders - Slate 600 */
    border: none;
    padding: 2px;
}
"""

    CONSOLIDATED_BUBBLE = """
QFrame { 
    border-radius: 5px; 
    background-color: #334155; /* Assistant Message Background - Slate 700 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    padding: 2px;
}
"""

    ROLLBACK_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 15px;
    padding: 8px;
    font-size: 24px;
    font-weight: bold;
    width: 30px;
    height: 30px;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
"""

    CONSOLIDATED_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 15px;
    padding: 8px;
    font-size: 16px;
    font-weight: bold;
    width: 30px;
    height: 30px;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
"""

    UNCONSOLIDATE_BUTTON = """
QPushButton {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
    color: #ffffff; /* White Text */
    border: none;
    border-radius: 15px;
    padding: 8px;
    font-size: 16px;
    font-weight: bold;
    width: 30px;
    height: 30px;
}
QPushButton:hover {
    background-color: #ef4444; /* Red hover for undo action */
}
QPushButton:pressed {
    background-color: #dc2626; /* Darker red for pressed */
}
"""

    # Tool dialog styles
    TOOL_DIALOG_TEXT_EDIT = """
QTextEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
    font-family: monospace;
}
QTextEdit:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
"""

    TOOL_DIALOG_YES_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    font-weight: bold;
    padding: 6px 14px;
    border: none;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
"""

    TOOL_DIALOG_ALL_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    font-weight: bold;
    padding: 6px 14px;
    border: none;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
"""

    TOOL_DIALOG_NO_BUTTON = """
QPushButton {
    background-color: #ef4444; /* Destructive/Error - Red 500 */
    color: #ffffff; /* White */
    font-weight: bold;
    padding: 6px 14px;
    border: none;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #dc2626; /* Darker red for hover */
}
"""

    AGENT_MENU_BUTTON = """
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
    padding-left: 12px; /* Add some padding for text */
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
QPushButton::menu-indicator {
    subcontrol-origin: padding;
    subcontrol-position: right center;
    right: 5px;
    width: 16px;
}
"""

    # Widget-specific styles
    SYSTEM_MESSAGE_LABEL = """
color: #94a3b8; /* Secondary Text - Slate 400 */
padding: 2px;
"""

    SYSTEM_MESSAGE_TOGGLE = """
QPushButton {
    background-color: transparent;
    color: #7fb239; /* Primary Green */
    border: none;
    text-align: left;
    padding: 2px;
}
QPushButton:hover {
    color: #638b2c; /* Secondary Green */
}
"""

    # Config window styles
    CONFIG_DIALOG = """
QDialog {
    background-color: #0f172a; /* Primary Background - Slate 900 */
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QTabWidget::pane {
    border: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    border-radius: 4px;
}
QTabBar::tab {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 8px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-bottom: none;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    border-bottom-color: #1e293b; /* Card/Container Background - Slate 800 */
    color: #7fb239; /* Primary Green */
}
QTabBar::tab:hover:!selected {
    background-color: #475569; /* Borders - Slate 600 */
}
QPushButton {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
    border: none;
    border-radius: 4px;
    padding: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:pressed {
    background-color: #638b2c; /* Secondary Green */
}
QPushButton:disabled {
    background-color: #475569; /* Borders - Slate 600 */
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
QListWidget {
    background-color: #0f172a; /* Primary Background - Slate 900 */
    border: 1px solid #334155; /* Secondary/Muted Background - Slate 700 */
    border-radius: 4px;
    padding: 4px;
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QListWidget::item {
    padding: 6px;
    border-radius: 2px;
    color: #f8fafc; /* Primary Text - Slate 50 */
    background-color: #0f172a; /* Primary Background - Slate 900 */
}
QListWidget::item:selected {
    background-color: #7fb239; /* Primary Green */
    color: #ffffff; /* Green on White Text */
}
QListWidget::item:hover:!selected {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
QLineEdit, QTextEdit {
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 6px;
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #7fb239; /* Primary Green */
}
QCheckBox {
    spacing: 8px;
    color: #f8fafc; /* Primary Text - Slate 50 */
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 2px;
    background-color: #475569; /* Borders - Slate 600 */
    border: 1px solid #64748b; /* Accent/Hover - Slate 500 */
}
QCheckBox::indicator:checked {
    background-color: #7fb239; /* Primary Green */
    border: 1px solid #7fb239; /* Primary Green */
}
QCheckBox::indicator:hover {
    border: 1px solid #638b2c; /* Secondary Green */
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 12px; /* Ensure space for title */
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left; /* position at the top left */
    padding: 0 4px 4px 4px; /* padding for title */
    color: #7fb239; /* Primary Green */
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    left: 10px; /* Adjust to align with content */
}
QScrollArea {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
    border: none;
}
/* Style for the QWidget inside QScrollArea if needed */
QScrollArea > QWidget > QWidget { /* Target the editor_widget */
     background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
QLabel {
    color: #f8fafc; /* Primary Text - Slate 50 */
    padding: 2px; /* Add some padding to labels */
}
QSplitter::handle {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
QSplitter::handle:hover {
    background-color: #475569; /* Borders - Slate 600 */
}
QSplitter::handle:pressed {
    background-color: #64748b; /* Accent/Hover - Slate 500 */
}
"""

    PANEL = """
background-color: #1e293b; /* Card/Container Background - Slate 800 */
"""

    SCROLL_AREA = """
background-color: #1e293b; /* Card/Container Background - Slate 800 */
border: none;
"""

    EDITOR_WIDGET = """
background-color: #1e293b; /* Card/Container Background - Slate 800 */
"""

    GROUP_BOX = """
background-color: #0f172a; /* Primary Background - Slate 900 */
"""

    SPLITTER_COLOR = """
QSplitter::handle {
    background-color: #1e293b; /* Card/Container Background - Slate 800 */
}
QSplitter::handle:hover {
    background-color: #334155; /* Secondary/Muted Background - Slate 700 */
}
QSplitter::handle:pressed {
    background-color: #475569; /* Borders - Slate 600 */
}
"""

    METADATA_HEADER_LABEL = """
QLabel {
    color: #94a3b8; /* Secondary Text - Slate 400 */
    font-style: italic;
    padding-bottom: 5px;
}
"""

    # Message label styles
    USER_MESSAGE_LABEL = """
QLabel {
    color: #ffffff; /* User Message Text - White */
}
"""

    ASSISTANT_MESSAGE_LABEL = """
QLabel {
    color: #f8fafc; /* Assistant Message Text - Slate 50 */
}
"""

    THINKING_MESSAGE_LABEL = """
QLabel {
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    # Sender label styles
    USER_SENDER_LABEL = """
QLabel {
    font-weight: bold;
    color: #ffffff; /* User Message Text - White */
    padding: 2px;
}
"""

    ASSISTANT_SENDER_LABEL = """
QLabel {
    font-weight: bold;
    color: #f8fafc; /* Assistant Message Text - Slate 50 */
    padding: 2px;
}
"""

    THINKING_SENDER_LABEL = """
QLabel {
    font-weight: bold;
    color: #94a3b8; /* Secondary Text - Slate 400 */
    padding: 2px;
}
"""

    # File display label styles
    USER_FILE_NAME_LABEL = """
QLabel {
    font-weight: bold;
    color: #ffffff; /* User Message Text - White */
    padding-left: 10px;
}
"""

    ASSISTANT_FILE_NAME_LABEL = """
QLabel {
    font-weight: bold;
    color: #f8fafc; /* Assistant Message Text - Slate 50 */
    padding-left: 10px;
}
"""

    USER_FILE_INFO_LABEL = """
QLabel {
    color: #ffffff; /* User Message Text - White */
}
"""

    ASSISTANT_FILE_INFO_LABEL = """
QLabel {
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    CODE_CSS = """
table td {border: 1px solid #f8fafc; padding: 5px;}
table { border-collapse: collapse; }
pre { line-height: 1; background-color: #1e293b; border-radius: 8px; padding: 12px; color: #f8fafc; white-space: pre-wrap; word-wrap: break-word; } /* Card Background, Primary Text */
td.linenos .normal { color: #94a3b8; background-color: transparent; padding-left: 5px; padding-right: 5px; } /* Secondary Text */
span.linenos { color: #94a3b8; background-color: transparent; padding-left: 5px; padding-right: 5px; } /* Secondary Text */
td.linenos .special { color: #f8fafc; background-color: #334155; padding-left: 5px; padding-right: 5px; } /* Primary Text, Secondary Background */
span.linenos.special { color: #f8fafc; background-color: #334155; padding-left: 5px; padding-right: 5px; } /* Primary Text, Secondary Background */
.codehilite .hll { background-color: #334155 } /* Secondary Background */
.codehilite { background: #1e293b; border-radius: 8px; padding: 10px; color: #f8fafc; } /* Card Background, Primary Text */
.codehilite .c { color: #94a3b8; font-style: italic } /* Comment -> Secondary Text */
.codehilite .err { border: 1px solid #ef4444; color: #ef4444; } /* Error -> Red */
.codehilite .k { color: #7fb239; font-weight: bold } /* Keyword -> Primary Green */
.codehilite .o { color: #638b2c } /* Operator -> Secondary Green */
.codehilite .ch { color: #94a3b8; font-style: italic } /* Comment.Hashbang -> Secondary Text */
.codehilite .cm { color: #94a3b8; font-style: italic } /* Comment.Multiline -> Secondary Text */
.codehilite .cp { color: #7fb239 } /* Comment.Preproc -> Primary Green */
.codehilite .cpf { color: #94a3b8; font-style: italic } /* Comment.PreprocFile -> Secondary Text */
.codehilite .c1 { color: #94a3b8; font-style: italic } /* Comment.Single -> Secondary Text */
.codehilite .cs { color: #94a3b8; font-style: italic } /* Comment.Special -> Secondary Text */
.codehilite .gd { color: #ef4444 } /* Generic.Deleted -> Red */
.codehilite .ge { font-style: italic } /* Generic.Emph */
.codehilite .ges { font-weight: bold; font-style: italic } /* Generic.EmphStrong */
.codehilite .gr { color: #ef4444 } /* Generic.Error -> Red */
.codehilite .gh { color: #7fb239; font-weight: bold } /* Generic.Heading -> Primary Green */
.codehilite .gi { color: #638b2c } /* Generic.Inserted -> Secondary Green */
.codehilite .go { color: #f8fafc } /* Generic.Output -> Primary Text */
.codehilite .gp { color: #7fb239; font-weight: bold } /* Generic.Prompt -> Primary Green */
.codehilite .gs { font-weight: bold } /* Generic.Strong */
.codehilite .gu { color: #7fb239; font-weight: bold } /* Generic.Subheading -> Primary Green */
.codehilite .gt { color: #ef4444 } /* Generic.Traceback -> Red */
.codehilite .kc { color: #7fb239; font-weight: bold } /* Keyword.Constant -> Primary Green */
.codehilite .kd { color: #7fb239; font-weight: bold } /* Keyword.Declaration -> Primary Green */
.codehilite .kn { color: #7fb239; font-weight: bold } /* Keyword.Namespace -> Primary Green */
.codehilite .kp { color: #7fb239 } /* Keyword.Pseudo -> Primary Green */
.codehilite .kr { color: #7fb239; font-weight: bold } /* Keyword.Reserved -> Primary Green */
.codehilite .kt { color: #64748b; font-weight: bold } /* Keyword.Type -> Accent */
.codehilite .m { color: #64748b } /* Literal.Number -> Accent */
.codehilite .s { color: #638b2c } /* Literal.String -> Secondary Green */
.codehilite .na { color: #64748b } /* Name.Attribute -> Accent */
.codehilite .nb { color: #7fb239 } /* Name.Builtin -> Primary Green */
.codehilite .nc { color: #7fb239; font-weight: bold } /* Name.Class -> Primary Green */
.codehilite .no { color: #64748b } /* Name.Constant -> Accent */
.codehilite .nd { color: #7fb239 } /* Name.Decorator -> Primary Green */
.codehilite .ni { color: #f8fafc; font-weight: bold } /* Name.Entity -> Primary Text */
.codehilite .ne { color: #ef4444; font-weight: bold } /* Name.Exception -> Red */
.codehilite .nf { color: #7fb239; font-weight: bold } /* Name.Function -> Primary Green */
.codehilite .nl { color: #f8fafc } /* Name.Label -> Primary Text */
.codehilite .nn { color: #7fb239; font-weight: bold } /* Name.Namespace -> Primary Green */
.codehilite .nt { color: #7fb239; font-weight: bold } /* Name.Tag -> Primary Green */
.codehilite .nv { color: #64748b } /* Name.Variable -> Accent */
.codehilite .ow { color: #638b2c; font-weight: bold } /* Operator.Word -> Secondary Green */
.codehilite .w { color: #475569 } /* Text.Whitespace -> Borders */
.codehilite .mb { color: #64748b } /* Literal.Number.Bin -> Accent */
.codehilite .mf { color: #64748b } /* Literal.Number.Float -> Accent */
.codehilite .mh { color: #64748b } /* Literal.Number.Hex -> Accent */
.codehilite .mi { color: #64748b } /* Literal.Number.Integer -> Accent */
.codehilite .mo { color: #64748b } /* Literal.Number.Oct -> Accent */
.codehilite .sa { color: #638b2c } /* Literal.String.Affix -> Secondary Green */
.codehilite .sb { color: #638b2c } /* Literal.String.Backtick -> Secondary Green */
.codehilite .sc { color: #638b2c } /* Literal.String.Char -> Secondary Green */
.codehilite .dl { color: #638b2c } /* Literal.String.Delimiter -> Secondary Green */
.codehilite .sd { color: #94a3b8; font-style: italic } /* Literal.String.Doc -> Secondary Text */
.codehilite .s2 { color: #638b2c } /* Literal.String.Double -> Secondary Green */
.codehilite .se { color: #64748b; font-weight: bold } /* Literal.String.Escape -> Accent */
.codehilite .sh { color: #638b2c } /* Literal.String.Heredoc -> Secondary Green */
.codehilite .si { color: #638b2c; font-weight: bold } /* Literal.String.Interpol -> Secondary Green */
.codehilite .sx { color: #638b2c } /* Literal.String.Other -> Secondary Green */
.codehilite .sr { color: #638b2c } /* Literal.String.Regex -> Secondary Green */
.codehilite .s1 { color: #638b2c } /* Literal.String.Single -> Secondary Green */
.codehilite .ss { color: #638b2c } /* Literal.String.Symbol -> Secondary Green */
.codehilite .bp { color: #7fb239 } /* Name.Builtin.Pseudo -> Primary Green */
.codehilite .fm { color: #7fb239; font-weight: bold } /* Name.Function.Magic -> Primary Green */
.codehilite .vc { color: #64748b } /* Name.Variable.Class -> Accent */
.codehilite .vg { color: #64748b } /* Name.Variable.Global -> Accent */
.codehilite .vi { color: #64748b } /* Name.Variable.Instance -> Accent */
.codehilite .vm { color: #64748b } /* Name.Variable.Magic -> Accent */
.codehilite .il { color: #64748b } /* Literal.Number.Integer.Long -> Accent */
"""

    # Tool widget styles
    TOOL_WIDGET = """
QWidget {
    background-color: transparent;
}
"""

    TOOL_CARD = """
QFrame#toolCard {
    border-radius: 6px;
    background-color: rgba(127, 178, 57, 0.08); /* Primary Green with transparency */
    border: 1px solid rgba(127, 178, 57, 0.4); /* Primary Green border */
    padding: 1px;
}
"""

    TOOL_CARD_ERROR = """
QFrame#toolCard {
    border-radius: 6px;
    background-color: rgba(239, 68, 68, 0.08); /* Red with transparency */
    border: 1px solid rgba(239, 68, 68, 0.4); /* Red border */
    padding: 1px;
}
"""

    TOOL_HEADER = """
QLabel {
    font-weight: 500;
    color: #94a3b8; /* Secondary Text - Slate 400 */
}
"""

    TOOL_TOGGLE_BUTTON = """
QPushButton {
    background-color: transparent;
    border: none;
    color: #94a3b8; /* Secondary Text - Slate 400 */
    font-weight: normal;
    font-size: 11px;
}
QPushButton:hover {
    color: #7fb239; /* Primary Green */
}
"""

    TOOL_STATUS = """
QLabel {
    font-weight: 500;
    padding: 2px;
    font-size: 11px;
}
QLabel[status="running"] {
    color: #7fb239; /* Primary Green */
}
QLabel[status="complete"] {
    color: #638b2c; /* Secondary Green */
}
QLabel[status="error"] {
    color: #ef4444; /* Red */
}
"""

    TOOL_CONTENT = """
QLabel {
    color: #94a3b8; /* Secondary Text - Slate 400 */
    padding: 1px;
    font-size: 11px;
}
QLabel[role="title"] {
    font-weight: 500;
    color: #f8fafc; /* Primary Text - Slate 50 */
    font-size: 12px;
}
QLabel[role="key"] {
    color: #7fb239; /* Primary Green */
    font-weight: 500;
    font-size: 11px;
}
QLabel[role="value"] {
    color: #94a3b8; /* Secondary Text - Slate 400 */
    font-size: 11px;
}
QLabel[role="error"] {
    color: #ef4444; /* Red */
    font-size: 11px;
}
"""

    TOOL_PROGRESS = """
QProgressBar {
    border: none;
    background-color: rgba(71, 85, 105, 0.4); /* Borders with transparency */
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #7fb239; /* Primary Green */
    border-radius: 5px;
}
"""

    TOOL_SEPARATOR = """
QFrame {
    background-color: rgba(127, 178, 57, 0.3); /* Primary Green with transparency */
    border: none;
}
"""

    # Tool icons (consistent across all themes)
    TOOL_ICONS = {
        "web_search": "🔍",
        "fetch_webpage": "🌐",
        "transfer": "↗️",
        "adapt": "🧠",
        "retrieve_memory": "💭",
        "forget_memory_topic": "🗑️",
        "analyze_repo": "📂",
        "read_file": "📄",
        "default": "🔧",  # Default icon for unspecified tools
    }

    # JSON Editor styles
    JSON_EDITOR_COLORS = {
        "background": "#475569",  # Input Fields - Slate 600
        "text": "#f8fafc",  # Primary Text - Slate 50
        "border": "#475569",  # Borders - Slate 600
        "string": "#638b2c",  # Secondary Green
        "number": "#64748b",  # Accent - Slate 500
        "keyword": "#7fb239",  # Primary Green
        "punctuation": "#f8fafc",  # Primary Text - Slate 50
        "error": "#ef4444",  # Red
    }

    JSON_EDITOR_STYLE = """
QPlainTextEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 12px;
    line-height: 1.4;
}
QPlainTextEdit:focus {
    border: 1px solid #7fb239; /* Primary Green focus border */
}
"""

    # Markdown Editor styles
    MARKDOWN_EDITOR_COLORS = {
        "background": "#475569",  # Input Fields - Slate 600
        "text": "#f8fafc",  # Primary Text - Slate 50
        "border": "#475569",  # Borders - Slate 600
        "header": "#7fb239",  # Primary Green - for headers
        "bold": "#64748b",  # Accent - Slate 500 - for bold text
        "italic": "#638b2c",  # Secondary Green - for italic text
        "code": "#7fb239",  # Primary Green - for code blocks
        "code_background": "#334155",  # Secondary Background - code background
        "link": "#7fb239",  # Primary Green - for links
        "image": "#638b2c",  # Secondary Green - for images
        "list": "#64748b",  # Accent - Slate 500 - for list markers
        "blockquote": "#638b2c",  # Secondary Green - for blockquotes
        "hr": "#94a3b8",  # Secondary Text - for horizontal rules
        "strikethrough": "#ef4444",  # Red - for strikethrough text
        "error": "#ef4444",  # Red - for errors
    }

    MARKDOWN_EDITOR_STYLE = """
QPlainTextEdit {
    background-color: #475569; /* Input Fields - Slate 600 */
    color: #f8fafc; /* Primary Text - Slate 50 */
    border: 1px solid #475569; /* Borders - Slate 600 */
    border-radius: 4px;
    padding: 8px;
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    font-size: 13px;
    line-height: 1.6;
    selection-background-color: #64748b; /* Accent - Slate 500 */
    selection-color: #f8fafc; /* Primary Text - Slate 50 */
}
QPlainTextEdit:focus {
    border: 1px solid #7fb239; /* Primary Green focus border */
}
"""
