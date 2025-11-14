---
name: zellij-config
description: Comprehensive Zellij terminal multiplexer configuration management. Use when the user needs to configure, customize, or enhance their Zellij setup including creating/modifying config.kdl files, building layouts with command panes and tabs, customizing themes and keybindings, setting up plugins, or implementing workspace automation. Triggers on requests about Zellij configuration, layout creation, theme customization, keybinding changes, or workspace setup.
license: MIT
metadata:
  version: 1.3
---

# Zellij Configuration Management

This skill provides comprehensive guidance for managing Zellij configurations, layouts, themes, and advanced features. Zellij is a terminal multiplexer written in Rust that uses KDL (KDL Document Language) for configuration.

## Configuration File Location

ALWAYS check for files LOCALLY, avoid checking in any kind of (remote) Docker container
Zellij configuration lives in `config.kdl`. The user's configuration directory is `~/dotfiles/.config/zellij/`.
The config file should be at `~/dotfiles/.config/zellij/config.kdl`.
IMPORTANT: to verify the existence of the config file `~/dotfiles/.config/zellij/config.kdl` REMEMBER that there’s a ‘.’ (dot) in the path so the file is HIDDEN.
IMPORTANT: to verify the existence of the config file `~/dotfiles/.config/zellij/config.kdl` REMEMBER that always use the ‘-a’ option when executing the ‘ls’ command.
NEVER use ‘ls’ WITHOUT the ‘-a’ option in this skill!

## Updates

Updates should be at `~/dotfiles/.config/zellij/config.kdl`.
If `~/dotfiles/.config/zellij/config.kdl` does NOT EXIST or is NOT FOUND, that is a RED FLAG. In that case, HALT the flow.
`~/dotfiles/` is managed by Git. Therefore, BEFORE doing anything, check whether there are any pending changes to commit and pull from Git to ENSURE the latest version is in place locally.

Zellij searches for configuration in this order:

1. `--config` flag path
2. `ZELLIJ_CONFIG_FILE` environment variable
3. `$HOME/.config/zellij/config.kdl` (macOS: `/Users/Alice/Library/Application Support/org.Zellij-Contributors.Zellij`)
4. System location `/etc/zellij`

## Core Configuration Management

### Live Configuration Updates

Zellij watches the active configuration file and applies most changes immediately without restart. Changes requiring restart are noted in comments.

### Key Configuration Options

See `references/config-options.md` for comprehensive configuration reference including:

- Display options (mouse_mode, pane_frames, theme)
- Buffer settings (scroll_buffer_size)
- Clipboard configuration (copy_command, copy_clipboard)
- Editor settings (scrollback_editor)
- Layout and theme directories
- Session behavior (mirror_session, default_mode, default_layout)

## Layout System

Layouts define pre-configured arrangements of panes, tabs, and commands for workflow automation.

### Creating Layouts

Layouts use KDL syntax with these core components:

**Basic pane structure:**

```kdl
layout {
    pane  // Empty shell pane
    pane split_direction="horizontal" {
        pane command="exa" { args "--color" "always" "-l" }
        pane command="git" { args "log" }
    }
}
```

**Editor panes:**

```kdl
pane edit="src/main.rs"  // Opens file in $EDITOR
```

**Command panes:**

```kdl
pane command="cargo" {
    args "test"
    start_suspended true  // Wait for Enter before running
    cwd "/path/to/project"  // Set working directory
    focus true  // Focus this pane on startup
}
```

### Layout Features

**Split directions**: `vertical` or `horizontal`
**Pane sizes**: Fixed numbers or percentages (e.g., `size="60%"` or `size=5`)
**Borderless panes**: `borderless=true` for UI elements
**Focus control**: `focus=true` to set initial focus

See `references/layout-examples.md` for comprehensive layout patterns including templates, tabs, and complex workflows.

### Loading Layouts

Load layout on session start:

```bash
zellij --layout /path/to/layout.kdl
# or with alias
zellij --layout https://example.com/layout.kdl
```

Apply layout in running session:

```bash
zellij action new-tab --layout /path/to/layout.kdl
```

Set default layout in config.kdl:

```kdl
default_layout "compact"
```

### Layout Templates

**Pane templates** avoid repetition:

```kdl
pane_template name="cargo-pane" {
    command "cargo"
    start_suspended true
}

cargo-pane { args "test" }
cargo-pane { args "run" }
```

**Tab templates** structure tabs:

```kdl
tab_template name="dev-tab" {
    pane size=1 borderless=true {
        plugin location="zellij:tab-bar"
    }
    children
    pane size=2 borderless=true {
        plugin location="zellij:status-bar"
    }
}
```

## Theme Customization

Themes define UI colors using KDL syntax. Themes can be defined in config.kdl or in separate files under `~/.config/zellij/themes/`.

### Theme Structure

```kdl
themes {
    my-theme {
        fg 248 248 242        // Foreground (RGB or HEX)
        bg 40 42 54           // Background
        red 255 85 85
        green 80 250 123
        yellow 241 250 140
        blue 98 114 164
        magenta 255 121 198
        orange 255 184 108
        cyan 139 233 253
        black 0 0 0
        white 255 255 255
    }
}

theme "my-theme"  // Activate theme
```

### Loading Themes

1. **In config.kdl**: Define theme in `themes {}` block and set `theme "name"`
2. **Separate files**: Place theme files in `~/.config/zellij/themes/` directory
3. **Command line**: `zellij options --theme my-theme`

Zellij includes built-in themes: default, dracula, gruvbox-dark, gruvbox-light, nord, tokyo-night, catppuccin, and more.

See `references/theme-components.md` for detailed UI component customization.

## Keybindings

Keybindings are organized by mode (normal, pane, tab, resize, scroll, etc.).

### Keybinding Structure

```kdl
keybinds {
    normal {
        bind "Alt n" { NewPane; }
        bind "Alt h" { MoveFocus "Left"; }
    }
    
    shared_except "locked" {
        bind "Ctrl g" { SwitchToMode "locked"; }
    }
}
```

### Custom Keybinding Example

```kdl
keybinds {
    normal clear-defaults=true {  // Remove default bindings
        bind "Alt q" { Quit; }
        bind "Alt d" { Detach; }
        bind "Alt p" { SwitchToMode "pane"; }
    }
    
    shared {  // Applies to all modes
        bind "Alt 1" { Run "git" "status"; }
        bind "Alt 2" { Run "git" "diff"; }
    }
}
```

### Including Keybindings in Layouts

Layouts can override configuration keybindings:

```kdl
layout {
    pane
    keybinds {
        shared {
            bind "Alt 1" { Run "npm" "test"; }
        }
    }
}
```

## Plugin Configuration

Plugins extend Zellij functionality. Built-in plugins include tab-bar, status-bar, strider (file picker), compact-bar, and session-manager.

### Plugin Aliases

```kdl
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:status-bar"
    strider location="zellij:strider"
    compact-bar location="zellij:compact-bar"
}
```

### Loading Plugins in Layouts

```kdl
pane size=1 borderless=true {
    plugin location="zellij:compact-bar"
}

pane {
    plugin location="file:/path/to/plugin.wasm"
}
```

### Background Plugins

Load plugins on session start:

```kdl
load_plugins {
    my-plugin location="https://example.com/plugin.wasm" {
        setting "value"
    }
}
```

## Advanced Features

### Command Panes

Command panes run specific commands and display exit codes:

- Press Enter to re-run command
- Exit code displayed when command completes
- Use `start_suspended=true` to wait before first run

### CWD Composition

Set working directories hierarchically:

```kdl
tab cwd="/project" {
    pane cwd="frontend"  // Resolves to /project/frontend
    pane cwd="backend"   // Resolves to /project/backend
}
```

### Session Management

```bash
zellij                      # Start new session
zellij attach              # Attach to existing
zellij attach session-name # Attach to specific session
zellij list-sessions       # List all sessions
zellij kill-session name   # Kill specific session
```

### CLI Control

```bash
zellij action new-tab
zellij action rename-tab "My Tab"
zellij action switch-mode locked
zellij run -- git status   # Run command in new pane
zellij edit file.rs        # Edit file in new pane
```

## Best Practices

1. **Start simple**: Begin with basic configuration, add complexity as needed
2. **Use templates**: DRY principle applies to layouts - use pane_template and tab_template
3. **Leverage command panes**: For development workflows, use command panes with start_suspended
4. **Organize layouts**: Store layouts in `~/.config/zellij/layouts/` for easy access
5. **Theme organization**: Keep themes in separate files for easier sharing
6. **Document custom keybindings**: Add comments in config.kdl for team sharing
7. **Test layouts**: Always test layouts in disposable sessions before committing
8. **Use CWD composition**: Reduce repetition in layouts with hierarchical paths

## Workflow Examples

See `references/workflow-examples.md` for complete examples including:

- Development environment layouts (Rust, Python, Node.js)
- DevOps layouts (monitoring, deployment)
- Content creation layouts (documentation, blogging)
- System administration layouts

## Troubleshooting

**Config not loading**: Check file location `~/dotfiles/.config/zellij/config.kdl` using ‘bash ls’ WITH the ‘-a' option
**Layout errors**: Validate KDL syntax, ensure quotes around strings
**Theme not applying**: Verify theme name matches definition, check spelling
**Keybindings not working**: Check for mode-specific bindings, verify clear-defaults setting
**Plugins not loading**: Ensure plugin location is accessible, check permissions

## Bundled Resources

### References

- `references/config-options.md` - Complete configuration option reference
- `references/layout-examples.md` - Comprehensive layout patterns and templates
- `references/theme-components.md` - Theme UI component customization guide
- `references/workflow-examples.md` - Complete workflow automation examples
