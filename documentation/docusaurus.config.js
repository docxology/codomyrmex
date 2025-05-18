/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Codomyrmex Documentation',
  tagline: 'Modular, Extensible Coding Workspace',
  favicon: 'img/favicon.ico', // You'll need to create this image

  // Set the production url of your site here
  url: 'https://your-codomyrmex-docs-url.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/codomyrmex/', // Adjust if deploying to a different path

  // GitHub pages deployment config.
  organizationName: 'your-github-org', // Replace with your GitHub org/user name
  projectName: 'codomyrmex', // Replace with your repo name

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
          // Please change this to your repo.
          editUrl: 'https://github.com/your-github-org/codomyrmex/tree/main/',
          routeBasePath: '/', // Serve docs at the site's root
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg', // You'll need to create this image
      navbar: {
        title: 'Codomyrmex',
        logo: {
          alt: 'Codomyrmex Logo',
          src: 'img/logo.svg', // You'll need to create this image
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Documentation',
          },
          // {to: '/blog', label: 'Blog', position: 'left'}, // If you enable blog
          {
            href: 'https://github.com/your-github-org/codomyrmex',
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
              // Add links to your community channels if any
              // {
              //   label: 'Stack Overflow',
              //   href: 'https://stackoverflow.com/questions/tagged/docusaurus',
              // },
            ],
          },
          {
            title: 'More',
            items: [
              // {label: 'Blog', to: '/blog'}, // If you enable blog
              {
                label: 'GitHub',
                href: 'https://github.com/your-github-org/codomyrmex',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Codomyrmex. Built with Docusaurus.`,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
      },
    }),
};

module.exports = config; 