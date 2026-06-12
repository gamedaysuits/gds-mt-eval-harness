// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'MT Eval Arena',
  tagline: 'Think you can solve it? Prove it.',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  // Production URL — custom domain
  url: 'https://mtevalarena.org',
  baseUrl: '/',
  trailingSlash: false,

  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'de', 'nl', 'fil', 'es', 'zh', 'ja', 'ko', 'pt', 'th', 'vi', 'ar'],
    localeConfigs: {
      en:  { label: 'English' },
      fr:  { label: 'Français' },
      de:  { label: 'Deutsch' },
      nl:  { label: 'Nederlands' },
      fil: { label: 'Filipino' },
      es:  { label: 'Español' },
      zh:  { label: '简体中文' },
      ja:  { label: '日本語' },
      ko:  { label: '한국어' },
      pt:  { label: 'Português' },
      th:  { label: 'ไทย' },
      vi:  { label: 'Tiếng Việt' },
      ar:  { label: 'العربية', direction: 'rtl' },
    },
  },

  // GitHub coordinates for "Edit this page" links
  organizationName: 'gamedaysuits',
  projectName: 'arena',

  onBrokenLinks: 'warn',

  // Preload the self-hosted variable fonts used above the fold
  // (Fraunces display serif + Inter UI — see static/fonts/LICENSES.md)
  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'preload',
        href: '/fonts/fraunces-latin-opsz-normal.woff2',
        as: 'font',
        type: 'font/woff2',
        crossorigin: 'anonymous',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'preload',
        href: '/fonts/inter-latin-opsz-normal.woff2',
        as: 'font',
        type: 'font/woff2',
        crossorigin: 'anonymous',
      },
    },
  ],

  // Enable Mermaid diagrams in Markdown
  markdown: {
    mermaid: true,
    format: 'detect',
  },
  themes: [
    '@docusaurus/theme-mermaid',
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // editUrl: 'https://github.com/gamedaysuits/Champollion/tree/main/website/',  // Re-enable when repo is public
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
      image: 'img/arena-social-card.png',

      colorMode: {
        defaultMode: 'dark',
        respectPrefersColorScheme: true,
      },

      navbar: {
        title: 'MT Eval Arena',
        logo: {
          alt: 'MT Eval Arena — rosetta stela mark, shared with champollion.dev',
          src: 'img/logo.svg',
          srcDark: 'img/logo-dark.svg',
          width: 28,
          height: 28,
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'arenaSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://champollion.dev/leaderboard',
            label: 'Leaderboard',
            position: 'left',
          },
          {
            href: 'https://champollion.dev',
            label: 'Champollion ↗',
            position: 'right',
          },
          {
            href: 'https://github.com/gamedaysuits/Champollion',
            label: 'GitHub',
            position: 'right',
          },
          {
            type: 'localeDropdown',
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
                label: 'What Is The Arena?',
                to: '/docs',
              },
              {
                label: 'Submit a Method',
                to: '/docs/getting-started/submit-a-method',
              },
              {
                label: 'Data Sovereignty',
                to: '/docs/sovereignty/data-sovereignty',
              },
            ],
          },
          {
            title: 'Specifications',
            items: [
              {
                label: 'Harness',
                to: '/docs/specifications/harness',
              },
              {
                label: 'Methods',
                to: '/docs/specifications/methods',
              },
              {
                label: 'Run Card',
                to: '/docs/specifications/run-card',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'Leaderboard',
                href: 'https://champollion.dev/leaderboard',
              },
              {
                label: 'Champollion',
                href: 'https://champollion.dev',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/gamedaysuits/Champollion',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Curtis Forbes. Built with Docusaurus.`,
      },

      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'json', 'toml', 'yaml', 'python'],
      },

      // Mermaid theme configuration
      mermaid: {
        theme: {light: 'neutral', dark: 'dark'},
      },
    }),
};

export default config;
