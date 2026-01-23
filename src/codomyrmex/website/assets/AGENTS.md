# Codomyrmex Agents - src/codomyrmex/website/assets

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

The assets directory contains static CSS stylesheets and JavaScript files for the Codomyrmex web dashboard. These assets provide the visual styling and client-side interactivity for all dashboard pages.

## Active Components

- `style.css` - Main CSS stylesheet with dark theme styling, card layouts, status badges, and responsive design
- `css/` - Additional CSS files directory
  - `css/style.css` - Extended styles for the web interface
- `js/` - JavaScript files directory
  - `js/app.js` - Client-side JavaScript for interactivity
- `SPEC.md` - Asset specification documentation

## Key Classes

Not applicable - this directory contains CSS and JavaScript assets, not Python classes.

## Operating Contracts

- CSS uses CSS custom properties (variables) for theming:
  - `--bg-color` - Background color (#0d1117)
  - `--card-bg` - Card background (#161b22)
  - `--text-primary` - Primary text color (#f0f6fc)
  - `--text-secondary` - Secondary text color (#8b949e)
  - `--accent-color` - Accent/link color (#58a6ff)
  - `--success-color` - Success indicator (#238636)
  - `--border-color` - Border color (#30363d)
  - `--font-family` - Font stack (Inter, system fonts)
- Responsive grid layout using CSS Grid with `minmax(300px, 1fr)`
- Card components with hover effects (translateY, box-shadow)
- Status badges with color variants (active, running, etc.)
- Assets are copied to `output/assets/` during website generation

## Signposting

- **Parent Directory**: [website/](../README.md) - Website generation module
- **Sibling Directories**:
  - [templates/](../templates/README.md) - Jinja2 HTML templates
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
