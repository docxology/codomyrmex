/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Codomyrmex Documentation',
  tagline: 'Modular, Extensible Coding Workspace',
  favicon: 'img/favicon.ico',

  url: 'https://YOUR_DOCS_URL.com',
  baseUrl: '/codomyrmex/',

  organizationName: 'YOUR_GITHUB_ORG_OR_USER',
  projectName: 'codomyrmex',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/YOUR_GITHUB_ORG_OR_USER/codomyrmex/tree/main/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'Codomyrmex',
        logo: {
          alt: 'Codomyrmex Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            href: 'https://github.com/YOUR_GITHUB_ORG_OR_USER/codomyrmex',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Introduction',
                to: '/',
              },
            ],
          },
          {
            title: 'Community',
            items: [
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/YOUR_GITHUB_ORG_OR_USER/codomyrmex',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Codomyrmex Project. Built with Docusaurus.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
      },
    }),
};

module.exports = config; 