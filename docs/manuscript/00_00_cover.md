```{=latex}
\begin{titlepage}
\thispagestyle{empty}
\begin{center}
\vspace*{0.35in}
\includegraphics[width=0.92\textwidth]{output/figures/cover.png}

\vspace{0.35in}
{\Huge\bfseries {{CONFIG_TITLE}}\par}
\vspace{0.14in}
{\Large {{CONFIG_SUBTITLE}}\par}
\vspace{0.08in}
{\large {{CONFIG_FIRST_AUTHOR}}\par}
\vspace{0.16in}
{\normalsize Date: {{CONFIG_PUBLICATION_DATE_DISPLAY}}\par}
{\normalsize ORCID: {{CONFIG_AUTHOR_ORCID}}\par}
{\normalsize DOI: {{CONFIG_DOI}}\par}
{\normalsize Repository: \href{https://github.com/{{CONFIG_GITHUB_REPOSITORY}}}{github.com/{{CONFIG_GITHUB_REPOSITORY}}}\par}
\vfill
{\small v{{CONFIG_VERSION}}\par}
\end{center}
\end{titlepage}
\clearpage
```

```{=html}
<section id="cover" class="manuscript-cover">
  <img src="figures/cover.png" alt="Codomyrmex cover art: a colony control plane with a bright kernel hub, seven subsystem nodes, and consequence trails." />
  <div class="cover-copy">
    <h1>{{CONFIG_TITLE}}</h1>
    <p class="cover-subtitle">{{CONFIG_SUBTITLE}}</p>
    <p class="cover-author">{{CONFIG_FIRST_AUTHOR}}</p>
    <dl>
      <dt>Date</dt><dd>{{CONFIG_PUBLICATION_DATE_DISPLAY}}</dd>
      <dt>ORCID</dt><dd>{{CONFIG_AUTHOR_ORCID}}</dd>
      <dt>DOI</dt><dd>{{CONFIG_DOI}}</dd>
      <dt>Repository</dt><dd><a href="https://github.com/{{CONFIG_GITHUB_REPOSITORY}}">github.com/{{CONFIG_GITHUB_REPOSITORY}}</a></dd>
      <dt>Version</dt><dd>v{{CONFIG_VERSION}}</dd>
    </dl>
  </div>
</section>
```
