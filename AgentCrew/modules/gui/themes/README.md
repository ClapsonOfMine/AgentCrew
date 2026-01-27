# AgentCrew GUI Themes

This directory contains the theming system for the AgentCrew GUI application.

## Available Themes

### 1. Catppuccin Theme (`catppuccin.py`)

- **Type**: Dark theme
- **Style**: Modern, vibrant dark theme with purple and blue accents
- **Usage**: Default dark theme, activated when `theme = "dark"` in config

### 2. Atom Light Theme (`atom_light.py`)

- **Type**: Light theme
- **Style**: Clean, minimalist light theme with blue accents
- **Usage**: Activated when `theme = "light"` in config

### 3. Nord Theme (`nord.py`)

- **Type**: Dark theme
- **Style**: Arctic-inspired color palette with cool blue/teal accents
- **Usage**: Activated when `theme = "nord"` in config
- **Color Palette**: Based on the official
  [Nord Color Palette](https://www.nordtheme.com/)

### 4. Dracula Theme (`dracula.py`) ⭐ **NEW**

- **Type**: Dark theme
- **Style**: Bold, vibrant dark theme with purple and pink accents
- **Usage**: Activated when `theme = "dracula"` in config
- **Color Palette**: Based on the official
  [Dracula Theme](https://draculatheme.com/contribute)

## Dracula Theme Details

The Dracula theme implements the complete official color palette:

### Color Groups

#### Base Colors

- `#282A36` - Background (Main application background)
- `#44475A` - Current Line (Secondary elements, input fields)
- `#F8F8F2` - Foreground (Text color)
- `#6272A4` - Comment (Secondary text, borders)

#### Accent Colors

- `#8BE9FD` - Cyan (Focus states, operators)
- `#50FA7B` - Green (Success states, strings)
- `#FFB86C` - Orange (Warnings, special text)
- `#FF79C6` - Pink (Keywords, special buttons)
- `#BD93F9` - Purple (Primary actions, functions)
- `#FF5555` - Red (Errors, delete actions)
- `#F1FA8C` - Yellow (Highlights, classes)

### Design Principles

1. **Bold Contrast**: High contrast for excellent readability
2. **Vibrant Accents**: Distinctive accent colors for UI elements
3. **Semantic Consistency**: Colors consistently represent actions and states
4. **Visual Unity**: Harmonious color combinations throughout the UI

## Nord Theme Details

The Nord theme implements the complete 16-color Nord palette:

### Color Groups

#### Polar Night (Dark Backgrounds)

- `#2e3440` - Polar Night 0 (Main backgrounds)
- `#3b4252` - Polar Night 1 (Secondary backgrounds)
- `#434c5e` - Polar Night 2 (Input backgrounds)
- `#4c566a` - Polar Night 3 (Borders, disabled states)

#### Snow Storm (Light Text)

- `#d8dee9` - Snow Storm 0 (Secondary text)
- `#e5e9f0` - Snow Storm 1 (Primary text)
- `#eceff4` - Snow Storm 2 (Highlighted text)

#### Frost (Blue Accents)

- `#8fbcbb` - Frost 0 (Hover states)
- `#88c0d0` - Frost 1 (Focus states, links)
- `#81a1c1` - Frost 2 (Active states)
- `#5e81ac` - Frost 3 (Primary actions)

#### Aurora (Semantic Colors)

- `#bf616a` - Aurora Red (Errors, stop actions)
- `#d08770` - Aurora Orange (Warnings, hover effects)
- `#ebcb8b` - Aurora Yellow (Classes, namespaces)
- `#a3be8c` - Aurora Green (Success, confirmations)
- `#b48ead` - Aurora Purple (Special actions)

### Design Principles

1. **Accessibility**: High contrast ratios for readability
2. **Consistency**: Semantic color usage across components
3. **Hierarchy**: Clear visual distinction between UI elements
4. **Aesthetics**: Balanced, arctic-inspired color harmony

## Usage

To use a specific theme in AgentCrew:

1. Set the theme in your global configuration:

   For Nord theme:

   ```toml
   [global_settings]
   theme = "nord"
   ```

   For Dracula theme:

   ```toml
   [global_settings]
   theme = "dracula"
   ```

2. Restart the application or reload the configuration

3. The application will automatically apply the Nord color scheme to all UI
   components

## Architecture

The theming system uses:

- **StyleProvider**: Central theme management class
- **Theme Classes**: Static classes containing CSS style definitions
- **Configuration Integration**: Automatic theme switching based on user
  preferences

Each theme class provides comprehensive styling for:

- Main application windows and containers
- Buttons (primary, secondary, stop, success, error)
- Input fields and text areas
- Menus and context menus
- Message bubbles and chat components
- Code syntax highlighting
- Configuration dialogs
- Status indicators and labels

## Adding New Themes

To add a new theme:

1. Create a new theme file (e.g., `mytheme.yaml`)
2. Implement a theme file with all required style constants
3. Document the theme configuration value

## Development Notes

- All themes use Qt CSS/QSS syntax
- Color values should be hex codes with comments for clarity
- Maintain consistency with existing theme patterns
- Test all UI components with the new theme
- Ensure accessibility standards are met

