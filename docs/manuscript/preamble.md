# LaTeX Preamble

This file contains LaTeX packages and commands that are automatically injected into the document compilation process.

> **Rendering Note**: This file is included by `scripts/compile_manuscript.py` before final Pandoc execution to generate the physical PDF holding this text.

```latex
% Core mathematics
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{amsthm}

% Document layout
\usepackage{geometry}
\geometry{margin=0.25in}
\usepackage{float}
\usepackage{graphicx}

% Tables
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}

% Code listings
\usepackage{listings}

% Typography and formatting
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{fontspec}
\setmainfont{STIX Two Text}
\setsansfont{STIX Two Text}
\setmonofont{Menlo}[Scale=MatchLowercase]
\usepackage{newunicodechar}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{≈}{\ensuremath{\approx}}
\newunicodechar{∈}{\ensuremath{\in}}
\newunicodechar{→}{\ensuremath{\rightarrow}}

% Cross-references and citations
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    allcolors=red,
    pdftitle={Codomyrmex},
    pdfauthor={Codomyrmex Authors},
    pdfsubject={Codomyrmex -- integrity-verified manuscript},
    pdfkeywords={codomyrmex, integrity, verification, manuscript}
}
% natbib omitted — pandoc --citeproc manages all citation formatting.
% Adding \usepackage{natbib} conflicts with citeproc and causes a fatal error.

% ── Unicode-capable mono font for code listings ──────────────────────
% JuliaMono preferred when installed (TeX Live 2026+). Uncomment the block
% below and install JuliaMono to get full math/Greek glyph coverage in code
% blocks. Without it xelatex falls back to its default mono font; the
% document still compiles correctly.
%
% \usepackage{fontspec}
% \setmonofont{JuliaMono-Regular}[
%   Path           = /usr/local/texlive/2026/texmf-dist/fonts/truetype/public/juliamono/,
%   Extension      = .ttf,
%   UprightFont    = *,
%   BoldFont       = JuliaMono-Bold,
%   ItalicFont     = JuliaMono-RegularItalic,
%   BoldItalicFont = JuliaMono-BoldItalic,
%   Scale          = MatchLowercase,
% ]
%
% Math font (requires \usepackage{unicode-math} above):
% \setmathfont{latinmodern-math.otf}
```
