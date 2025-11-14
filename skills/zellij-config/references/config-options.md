# Zellij Configuration Options Reference

This reference covers all configuration options available in `config.kdl`.

## Display Options

### mouse_mode

Enable or disable mouse support.

- **Type**: boolean
- **Default**: `true`
- **Example**: `mouse_mode false`
- **Restart required**: No
- **Note**: May interfere with text selection in some terminals

### pane_frames

Toggle frames around panes.

- **Type**: boolean
- **Default**: `true`
- **Example**: `pane_frames false`
- **Restart required**: No

### simplified_ui

Request simplified UI from plugins (no arrow fonts).

- **Type**: boolean
- **Default**: `false`
- **Example**: `simplified_ui true`
- **Restart required**: No

### styled_underlines

Enable styled and colored underlines (undercurl).

- **Type**: boolean
- **Default**: `true`
- **Example**: `styled_underlines false`
- **Restart required**: Yes
- **Note**: Disable for terminals that don't support this feature

## Buffer and Performance

### scroll_buffer_size

Number of scrollback lines per pane.

- **Type**: positive integer
- **Default**: `10000`
- **Example**: `scroll_buffer_size 50000`
- **Restart required**: Yes
- **Note**: Lines are discarded in FIFO fashion

### scrollback_lines_to_serialize

Scrollback lines to save when serializing.

- **Type**: positive integer
- **Default**: `10000`
- **Example**: `scrollback_lines_to_serialize 5000`
- **Restart required**: Yes

## Clipboard and Copy

### copy_command

Command to execute for copying text.

- **Type**: string (command path)
- **Default**: None (uses OSC 52 ANSI control)
- **Example (macOS)**: `copy_command "pbcopy"`
- **Example (X11)**: `copy_command "xclip -selection clipboard"`
- **Example (Wayland)**: `copy_command "wl-copy"`
- **Restart required**: No

### copy_clipboard

Choose clipboard destination (X11/Wayland only).

- **Type**: "system" or "primary"
- **Default**: `"system"`
- **Example**: `copy_clipboard "primary"`
- **Restart required**: No
- **Note**: Ignored when using copy_command

### copy_on_select

Automatically copy selection on mouse release.

- **Type**: boolean
- **Default**: `true`
- **Example**: `copy_on_select false`
- **Restart required**: No

## Editor Configuration

### scrollback_editor

Editor for viewing pane scrollback.

- **Type**: string (path to editor)
- **Default**: `$EDITOR` or `$VISUAL`
- **Example**: `scrollback_editor "/usr/bin/nvim"`
- **Restart required**: No

### default_shell

Default shell for new panes.

- **Type**: string (path to shell)
- **Default**: `$SHELL`
- **Example**: `default_shell "fish"`
- **Restart required**: No

## Directory Configuration

### layout_dir

Directory for layout files.

- **Type**: string (path)
- **Default**: `$CONFIG_DIR/layouts`
- **Example**: `layout_dir "/path/to/layouts"`
- **Restart required**: Yes

### theme_dir

Directory for theme files.

- **Type**: string (path)
- **Default**: `$CONFIG_DIR/themes`
- **Example**: `theme_dir "/path/to/themes"`
- **Restart required**: Yes

## Theme Selection

### theme

Active theme name.

- **Type**: string (theme name)
- **Default**: `"default"`
- **Example**: `theme "dracula"`
- **Restart required**: No (live reload)
- **Note**: Theme must be defined in themes block or in theme_dir

## Layout and Mode

### default_layout

Layout to load on startup.

- **Type**: string (layout name)
- **Default**: `"default"`
- **Example**: `default_layout "compact"`
- **Restart required**: Yes

### default_mode

Starting input mode.

- **Type**: "normal", "locked", "pane", "tab", "scroll", "resize", "move", "session"
- **Default**: `"normal"`
- **Example**: `default_mode "locked"`
- **Restart required**: No

## Session Behavior

### mirror_session

Mirror cursor in multiplayer sessions.

- **Type**: boolean
- **Default**: `false`
- **Example**: `mirror_session true`
- **Restart required**: Yes
- **Note**: When true, all users share same cursor position

### on_force_close

Behavior on SIGTERM/SIGINT/SIGQUIT/SIGHUP.

- **Type**: "detach" or "quit"
- **Default**: `"detach"`
- **Example**: `on_force_close "quit"`
- **Restart required**: No

### session_name

Default session name.

- **Type**: string
- **Default**: Auto-generated
- **Example**: `session_name "my-session"`
- **Restart required**: No

### hide_session_name

Hide session name from UI.

- **Type**: boolean
- **Default**: `false`
- **Example**: `hide_session_name true`
- **Restart required**: No

## UI Configuration

### ui

Advanced UI configuration block.

- **Type**: nested KDL block
- **Example**:

```kdl
ui {
    pane_frames {
        rounded_corners true
        hide_session_name false
    }
}
```

- **Restart required**: Varies by option

## Environment Variables

### env

Set environment variables for panes.

- **Type**: KDL block with key-value pairs
- **Example**:

```kdl
env {
    RUST_LOG "info"
    NODE_ENV "development"
}
```

- **Restart required**: Yes

## Complete Example Configuration

```kdl
// Display
theme "gruvbox-dark"
pane_frames true
mouse_mode true
simplified_ui false
styled_underlines true

// Performance
scroll_buffer_size 20000
scrollback_lines_to_serialize 10000

// Clipboard
copy_command "pbcopy"  // macOS
copy_on_select true

// Editor
scrollback_editor "/usr/bin/nvim"
default_shell "fish"

// Directories
layout_dir "~/.config/zellij/layouts"
theme_dir "~/.config/zellij/themes"

// Behavior
default_layout "compact"
default_mode "normal"
mirror_session false
on_force_close "detach"

// Environment
env {
    EDITOR "nvim"
    VISUAL "nvim"
}
```

## Configuration Precedence

1. Command-line flags (highest)
2. Layout configuration (when loading layout)
3. Config file (config.kdl)
4. Default values (lowest)

## Validation

Check configuration validity:

```bash
zellij setup --check
```

Dump current configuration:

```bash
zellij setup --dump-config
```
