# Zellij Theme Components Reference

Comprehensive guide to customizing Zellij UI components through themes.

## Theme Structure

A theme consists of UI component definitions with color specifications for different parts of each
component.

```kdl
themes {
    my-theme {
        // UI component definitions
        ribbon_unselected { /* ... */ }
        ribbon_selected { /* ... */ }
        // ... more components
    }
}
```

## Color Format

Colors can be specified in two formats:

**RGB (space-separated values):**

```kdl
fg 248 248 242
```

**HEX (string):**

```kdl
fg "#F8F8F2"
```

## Core UI Components

### ribbon_unselected

Unselected ribbons in tab bar and status bar (inactive tabs, non-active modes).

**Attributes:**

- `base` - Base text color
- `background` - Background color
- `emphasis_0` - Primary accent color
- `emphasis_1` - Secondary accent color
- `emphasis_2` - Tertiary accent color
- `emphasis_3` - Quaternary accent color

**Example:**

```kdl
ribbon_unselected {
    base 0 0 0
    background 255 153 0
    emphasis_0 255 53 94
    emphasis_1 255 255 255
    emphasis_2 0 217 227
    emphasis_3 255 0 255
}
```

### ribbon_selected

Selected ribbons (active tab, current mode indicator).

```kdl
ribbon_selected {
    base 0 0 0
    background 0 217 227
    emphasis_0 255 53 94
    emphasis_1 255 255 255
    emphasis_2 255 153 0
    emphasis_3 255 0 255
}
```

### bar_unselected

Status bar when not in focus.

```kdl
bar_unselected {
    base 248 248 242
    background 40 42 54
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

### bar_selected

Status bar when focused or active.

```kdl
bar_selected {
    base 248 248 242
    background 68 71 90
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

### text_unselected

Bare text in UI (modifier indicators, labels).

```kdl
text_unselected {
    base 248 248 242
    background 40 42 54
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

### text_selected

Text when selected or highlighted.

```kdl
text_selected {
    base 248 248 242
    background 68 71 90
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

### table_title

Table header/title styling.

```kdl
table_title {
    base 248 248 242
    background 40 42 54
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

### table_selected

Selected table cells.

```kdl
table_selected {
    base 0 0 0
    background 0 217 227
    emphasis_0 255 53 94
    emphasis_1 255 255 255
    emphasis_2 255 153 0
    emphasis_3 255 0 255
}
```

### table_unselected

Unselected table cells.

```kdl
table_unselected {
    base 248 248 242
    background 40 42 54
    emphasis_0 255 85 85
    emphasis_1 80 250 123
    emphasis_2 241 250 140
    emphasis_3 98 114 164
}
```

## Terminal Colors

Basic ANSI color palette for terminal content.

```kdl
fg 248 248 242      // Foreground text
bg 40 42 54         // Background
black 0 0 0         // ANSI black
red 255 85 85       // ANSI red
green 80 250 123    // ANSI green
yellow 241 250 140  // ANSI yellow
blue 98 114 164     // ANSI blue
magenta 177 98 134  // ANSI magenta
orange 255 184 108  // Orange (extended)
cyan 139 233 253    // ANSI cyan
white 255 255 255   // ANSI white
```

## Multiplayer User Colors

Colors assigned to users in collaborative sessions.

```kdl
multiplayer_user_colors {
    player_1 255 0 255
    player_2 0 217 227
    player_3 0 255 0
    player_4 255 230 0
    player_5 0 229 229
    player_6 0 0 255
    player_7 255 53 94
    player_8 0 255 255
    player_9 0 128 0
    player_10 0 0 128
}
```

## Complete Theme Examples

### Dracula Theme

```kdl
themes {
    dracula {
        // Terminal colors
        fg 248 248 242
        bg 40 42 54
        black 0 0 0
        red 255 85 85
        green 80 250 123
        yellow 241 250 140
        blue 98 114 164
        magenta 255 121 198
        orange 255 184 108
        cyan 139 233 253
        white 255 255 255
        
        // UI components
        ribbon_unselected {
            base 0 0 0
            background 255 153 0
            emphasis_0 255 53 94
            emphasis_1 255 255 255
            emphasis_2 0 217 227
            emphasis_3 255 0 255
        }
        
        ribbon_selected {
            base 0 0 0
            background 0 217 227
            emphasis_0 255 53 94
            emphasis_1 255 255 255
            emphasis_2 255 153 0
            emphasis_3 255 0 255
        }
        
        bar_unselected {
            base 248 248 242
            background 40 42 54
            emphasis_0 255 85 85
            emphasis_1 80 250 123
            emphasis_2 241 250 140
            emphasis_3 98 114 164
        }
        
        bar_selected {
            base 248 248 242
            background 68 71 90
            emphasis_0 255 85 85
            emphasis_1 80 250 123
            emphasis_2 241 250 140
            emphasis_3 98 114 164
        }
    }
}
```

### Gruvbox Dark Theme

```kdl
themes {
    gruvbox-dark {
        fg "#D5C4A1"
        bg "#282828"
        black "#3C3836"
        red "#CC241D"
        green "#98971A"
        yellow "#D79921"
        blue "#3C8588"
        magenta "#B16286"
        cyan "#689D6A"
        white "#FBF1C7"
        orange "#D65D0E"
    }
}
```

### Nord Theme

```kdl
themes {
    nord {
        fg "#D8DEE9"
        bg "#2E3440"
        black "#3B4252"
        red "#BF616A"
        green "#A3BE8C"
        yellow "#EBCB8B"
        blue "#81A1C1"
        magenta "#B48EAD"
        cyan "#88C0D0"
        white "#E5E9F0"
        orange "#D08770"
    }
}
```

### Custom High-Contrast Theme

```kdl
themes {
    high-contrast {
        // Bright text on dark background
        fg 255 255 255
        bg 0 0 0
        
        // Vivid ANSI colors
        black 0 0 0
        red 255 0 0
        green 0 255 0
        yellow 255 255 0
        blue 0 0 255
        magenta 255 0 255
        cyan 0 255 255
        white 255 255 255
        orange 255 165 0
        
        // High contrast UI
        ribbon_unselected {
            base 255 255 255
            background 50 50 50
            emphasis_0 255 0 0
            emphasis_1 0 255 0
            emphasis_2 0 0 255
            emphasis_3 255 255 0
        }
        
        ribbon_selected {
            base 0 0 0
            background 255 255 0
            emphasis_0 255 0 0
            emphasis_1 0 255 0
            emphasis_2 0 0 255
            emphasis_3 255 165 0
        }
    }
}
```

## Theme Development Workflow

### 1. Start with Base Colors

Begin by defining terminal colors that match your desired palette:

```kdl
themes {
    my-theme {
        fg "#FFFFFF"
        bg "#000000"
        // Define all ANSI colors...
    }
}
```

### 2. Test Terminal Colors

Set the theme and open a terminal to verify colors:

```bash
zellij options --theme my-theme
```

### 3. Customize UI Components

Add UI component definitions incrementally:

```kdl
themes {
    my-theme {
        // Terminal colors (from step 1)
        fg "#FFFFFF"
        // ...
        
        // Add UI components
        ribbon_selected {
            // Your colors
        }
    }
}
```

### 4. Use Theme Tester Plugin

Install and use the theme tester plugin for live preview:

```kdl
pane {
    plugin location="https://github.com/imsnif/theme-tester/releases/latest/download/theme-tester.wasm"
}
```

### 5. Iterate with Live Reload

With theme defined in config.kdl, Zellij automatically reloads changes. Edit theme, save, see results
immediately.

## Theme Organization

### Single File (config.kdl)

```kdl
themes {
    theme-one { /* ... */ }
    theme-two { /* ... */ }
}

theme "theme-one"
```

### Separate Files

**~/.config/zellij/themes/my-theme.kdl:**

```kdl
themes {
    my-theme {
        // Theme definition
    }
}
```

**config.kdl:**

```kdl
theme "my-theme"
```

## Tips for Creating Themes

1. **Start from existing theme**: Copy a similar theme and modify
2. **Use consistent color palette**: Pick 8-10 core colors and reuse them
3. **Test contrast ratios**: Ensure text is readable on backgrounds
4. **Consider colorblind users**: Don't rely solely on color for differentiation
5. **Test in different lighting**: Verify theme works in bright and dim environments
6. **Document your palette**: Add comments explaining color choices
7. **Share your themes**: Contribute to the community theme collection

## Color Palette Resources

- **Color Hunt**: <https://colorhunt.co/>
- **Coolors**: <https://coolors.co/>
- **Adobe Color**: <https://color.adobe.com/>
- **Terminal Sexy**: <https://terminal.sexy/>
- **Base16**: <https://github.com/chriskempson/base16>

## Built-in Themes

Zellij includes several built-in themes:

- `default`
- `dracula`
- `gruvbox-dark`
- `gruvbox-light`
- `nord`
- `tokyo-night`
- `catppuccin`
- `monokai`
- `solarized-dark`
- `solarized-light`

View theme source for reference:

```bash
zellij setup --dump-config | grep -A 100 "themes {"
```
