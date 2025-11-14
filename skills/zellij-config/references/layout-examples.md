# Zellij Layout Examples and Patterns

Comprehensive collection of layout patterns and real-world examples.

## Basic Layouts

### Simple Split Layout

```kdl
layout {
    pane split_direction="vertical" {
        pane
        pane
    }
}
```

### Three-Pane Development Layout

```kdl
layout {
    pane split_direction="vertical" {
        pane  // Main editor
        pane split_direction="horizontal" {
            pane  // Terminal
            pane  // Logs
        }
    }
}
```

### Grid Layout (2x2)

```kdl
layout {
    pane split_direction="vertical" {
        pane split_direction="horizontal" {
            pane
            pane
        }
        pane split_direction="horizontal" {
            pane
            pane
        }
    }
}
```

## Development Workflows

### Rust Development

```kdl
layout {
    pane size=1 borderless=true {
        plugin location="zellij:tab-bar"
    }
    
    pane split_direction="vertical" size="60%" {
        pane edit="src/main.rs"
        pane edit="Cargo.toml"
    }
    
    pane split_direction="vertical" size="40%" {
        pane command="cargo" {
            args "run"
            start_suspended true
            focus true
        }
        pane command="cargo" {
            args "test"
            start_suspended true
        }
        pane command="cargo" {
            args "check"
            start_suspended true
        }
    }
    
    pane size=2 borderless=true {
        plugin location="zellij:status-bar"
    }
}
```

### Python Development

```kdl
layout {
    tab name="Dev" {
        pane split_direction="vertical" {
            pane edit="app.py" size="60%"
            pane split_direction="horizontal" {
                pane command="python" {
                    args "-m" "pytest" "--watch"
                    start_suspended true
                }
                pane command="python" {
                    args "app.py"
                    start_suspended true
                }
            }
        }
    }
    
    tab name="Shell" {
        pane
    }
}
```

### Node.js/TypeScript Development

```kdl
layout {
    pane split_direction="vertical" {
        pane edit="src/index.ts" size="65%"
        pane split_direction="horizontal" size="35%" {
            pane command="npm" {
                args "run" "dev"
                start_suspended true
            }
            pane command="npm" {
                args "test" "--" "--watch"
                start_suspended true
            }
        }
    }
}
```

## Using Templates

### Pane Templates

```kdl
layout {
    // Define reusable pane template
    pane_template name="git-command" {
        command "git"
        cwd "."
    }
    
    // Define cargo template
    pane_template name="cargo-suspended" {
        command "cargo"
        start_suspended true
    }
    
    // Use templates
    pane split_direction="horizontal" {
        git-command { args "status" }
        git-command { args "log" "--oneline" }
    }
    
    pane split_direction="horizontal" {
        cargo-suspended { args "build" }
        cargo-suspended { args "test" }
        cargo-suspended { args "run" }
    }
}
```

### Tab Templates

```kdl
layout {
    // Define tab template
    tab_template name="ui-tab" {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }
    
    // Use template for multiple tabs
    ui-tab name="Editor" {
        pane edit="main.rs"
    }
    
    ui-tab name="Terminal" {
        pane
    }
    
    ui-tab name="Tests" {
        pane command="cargo" {
            args "test"
        }
    }
}
```

## Complex Workflows

### Multi-Service Development

```kdl
layout {
    tab_template name="service-tab" {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
    }
    
    default_tab_template {
        service-tab
    }
    
    service-tab name="Frontend" cwd="./frontend" {
        pane split_direction="vertical" {
            pane edit="src/App.tsx" size="70%"
            pane command="npm" {
                args "run" "dev"
                start_suspended true
            }
        }
    }
    
    service-tab name="Backend" cwd="./backend" {
        pane split_direction="vertical" {
            pane edit="src/main.rs" size="70%"
            pane command="cargo" {
                args "run"
                start_suspended true
            }
        }
    }
    
    service-tab name="Database" {
        pane split_direction="horizontal" {
            pane command="docker" {
                args "logs" "-f" "postgres"
            }
            pane  // psql client
        }
    }
    
    service-tab name="Monitoring" {
        pane split_direction="horizontal" {
            pane command="htop"
            pane command="docker" {
                args "stats"
            }
        }
    }
}
```

### Full-Stack Project

```kdl
layout {
    pane_template name="editor-with-term" split_direction="vertical" {
        pane edit size="60%"
        pane command size="40%"
    }
    
    tab name="Code" focus=true {
        editor-with-term {
            pane edit="src/main.ts"
            pane command="npm" {
                args "run" "dev"
                start_suspended true
            }
        }
    }
    
    tab name="API" cwd="api" {
        editor-with-term {
            pane edit="routes/index.ts"
            pane command="npm" {
                args "run" "dev"
                start_suspended true
            }
        }
    }
    
    tab name="Database" {
        pane split_direction="horizontal" {
            pane  // SQL shell
            pane command="docker" {
                args "exec" "-it" "postgres" "psql"
            }
        }
    }
    
    tab name="Git" {
        pane split_direction="horizontal" {
            pane command="git" {
                args "log" "--oneline" "--graph" "--all"
            }
            pane command="git" {
                args "status"
            }
        }
    }
}
```

## DevOps Layouts

### Infrastructure Monitoring

```kdl
layout {
    tab name="System" {
        pane split_direction="horizontal" {
            pane command="htop"
            pane command="watch" {
                args "-n" "2" "df" "-h"
            }
        }
    }
    
    tab name="Network" {
        pane split_direction="horizontal" {
            pane command="nethogs"
            pane command="iftop"
        }
    }
    
    tab name="Containers" {
        pane split_direction="vertical" {
            pane command="docker" {
                args "ps" "-a"
            }
            pane command="docker" {
                args "stats"
            }
        }
    }
    
    tab name="Logs" {
        pane command="tail" {
            args "-f" "/var/log/syslog"
        }
    }
}
```

### Kubernetes Operations

```kdl
layout {
    tab name="Pods" {
        pane split_direction="horizontal" {
            pane command="kubectl" {
                args "get" "pods" "-w"
            }
            pane  // kubectl commands
        }
    }
    
    tab name="Services" {
        pane command="kubectl" {
            args "get" "services" "-w"
        }
    }
    
    tab name="Logs" {
        pane  // pod log viewer
    }
}
```

## Special Patterns

### File Browser Integration

```kdl
layout {
    pane split_direction="vertical" {
        pane size="20%" {
            plugin location="zellij:strider" {
                cwd "/"
            }
        }
        pane size="80%" {
            pane
        }
    }
}
```

### Floating Panes

```kdl
layout {
    pane
    
    floating_panes {
        pane {
            x 10
            y 10
            width "50%"
            height "50%"
            command "htop"
        }
    }
}
```

### Nested Layout with CWD Composition

```kdl
layout {
    tab name="Project" cwd="~/projects/myapp" {
        pane split_direction="vertical" {
            pane cwd="frontend" {
                // Resolves to ~/projects/myapp/frontend
                edit "src/App.tsx"
            }
            pane cwd="backend" {
                // Resolves to ~/projects/myapp/backend
                command "cargo" {
                    args "watch" "-x" "run"
                }
            }
        }
    }
}
```

## Including Configuration in Layouts

### Custom Keybindings

```kdl
layout {
    pane
    
    keybinds {
        shared {
            bind "Alt 1" { Run "git" "status"; }
            bind "Alt 2" { Run "git" "diff"; }
            bind "Alt 3" { Run "npm" "test"; }
            bind "Alt 4" { Run "npm" "run" "build"; }
        }
    }
}
```

### Theme Override

```kdl
layout {
    pane
    
    theme "gruvbox-dark"
}
```

## Best Practices

1. **Use templates for repetition**: Define pane_template or tab_template for repeated patterns
2. **Start suspended for commands**: Use `start_suspended true` to prevent commands running immediately
3. **Leverage CWD composition**: Set base directory at tab level, relative paths at pane level
4. **Add UI components**: Include tab-bar and status-bar for better UX
5. **Focus control**: Use `focus true` on the primary working pane
6. **Size percentages**: Use percentages for responsive layouts that adapt to terminal size
7. **Borderless plugins**: Always use `borderless=true` for UI plugin panes
8. **Test incrementally**: Build layouts step by step, testing at each stage

## Layout File Organization

Store layouts in `~/.config/zellij/layouts/`:

```text
~/.config/zellij/layouts/
├── rust-dev.kdl
├── python-dev.kdl
├── monitoring.kdl
├── fullstack.kdl
└── personal/
    ├── blog.kdl
    └── notes.kdl
```

Load with:

```bash
zellij --layout rust-dev
# or
zellij action new-tab --layout monitoring
```
