import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Translate, {translate} from '@docusaurus/Translate';
import styles from './index.module.css';

/**
 * Landing page for mtevalarena.org
 *
 * Intentionally minimal — "coming soon" with the key pitch points
 * and links to the docs that already exist. All user-facing strings
 * are wrapped with <Translate> for i18n support.
 */

function HeroSection() {
  const {siteConfig} = useDocusaurusContext();

  return (
    <header className={styles.hero}>
      <div className={styles.heroInner}>
        <h1 className={styles.heroTitle}>{siteConfig.title}</h1>
        <p className={styles.heroTagline}>{siteConfig.tagline}</p>
        <p className={styles.heroSubtext}>
          <Translate id="homepage.hero.subtext">
            An open proving ground for machine translation methods — especially
            for languages that commercial services will never support.
          </Translate>
        </p>

        <div className={styles.heroCta}>
          <a href="/docs" className={styles.ctaPrimary}>
            <Translate id="homepage.cta.docs">Read the Docs</Translate>
          </a>
          <a
            href="https://github.com/gamedaysuits/Champollion"
            className={styles.ctaSecondary}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Translate id="homepage.cta.github">View on GitHub</Translate>
          </a>
        </div>

        <div className={styles.badge}>
          <span className={styles.badgeLabel}>
            <Translate id="homepage.badge.label">Status</Translate>
          </span>
          <span className={styles.badgeValue}>
            <Translate id="homepage.badge.value">Pre-release — Coming Soon</Translate>
          </span>
        </div>
      </div>
    </header>
  );
}

function PitchSection() {
  // Card data uses translate() for string extraction.
  // Docusaurus extracts these at build time into the JSON translation files.
  const cards = [
    {
      icon: '📐',
      title: translate({id: 'homepage.pitch.benchmarks.title', message: 'Standardized Benchmarks'}),
      description: translate({
        id: 'homepage.pitch.benchmarks.description',
        message: 'Reproducible evaluation with chrF++, exact match, FST acceptance, semantic scoring, and bootstrap confidence intervals. Every run is fingerprinted.',
      }),
    },
    {
      icon: '🏴',
      title: translate({id: 'homepage.pitch.sovereignty.title', message: 'Community Sovereignty'}),
      description: translate({
        id: 'homepage.pitch.sovereignty.description',
        message: 'Winning methods transfer ownership to the language community. OCAP® principles. Communities control their data, their methods, and their revenue.',
      }),
    },
    {
      icon: '🔌',
      title: translate({id: 'homepage.pitch.plugin.title', message: 'Open Plugin Architecture'}),
      description: translate({
        id: 'homepage.pitch.plugin.description',
        message: 'Bring any method: coached LLM, fine-tuned model, FST-gated pipeline, or custom plugin. If it produces translations, the harness can score it.',
      }),
    },
    {
      icon: '🚀',
      title: translate({id: 'homepage.pitch.bridge.title', message: 'Deployment Bridge'}),
      description: translate({
        id: 'homepage.pitch.bridge.description',
        message: 'Proven methods deploy to production via champollion. Developers consume via API. Revenue flows back to the community.',
      }),
    },
  ];

  return (
    <section className={styles.pitch}>
      <div className={styles.pitchGrid}>
        {cards.map((card, idx) => (
          <div key={idx} className={styles.pitchCard}>
            <div className={styles.pitchIcon}>{card.icon}</div>
            <h3 className={styles.pitchTitle}>{card.title}</h3>
            <p className={styles.pitchDescription}>{card.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function CurrentBenchmarks() {
  return (
    <section className={styles.benchmarks}>
      <h2 className={styles.sectionTitle}>
        <Translate id="homepage.benchmarks.title">Current Benchmarks</Translate>
      </h2>
      <div className={styles.benchmarkGrid}>
        <div className={styles.benchmarkCard}>
          <h3>EDTeKLA Dev Set v1</h3>
          <ul>
            <li><strong><Translate id="homepage.benchmarks.language">Language:</Translate></strong> <Translate id="homepage.benchmarks.edtekla.language">English → Plains Cree (SRO)</Translate></li>
            <li><strong><Translate id="homepage.benchmarks.entries">Entries:</Translate></strong> <Translate id="homepage.benchmarks.edtekla.entries">124 curated pairs</Translate></li>
            <li><strong><Translate id="homepage.benchmarks.license">License:</Translate></strong> CC BY-NC-SA 4.0</li>
            <li><strong><Translate id="homepage.benchmarks.source">Source:</Translate></strong> <Translate id="homepage.benchmarks.edtekla.source">University of Alberta</Translate></li>
          </ul>
        </div>
        <div className={styles.benchmarkCard}>
          <h3>FLORES+ Devtest</h3>
          <ul>
            <li><strong><Translate id="homepage.benchmarks.languages">Languages:</Translate></strong> <Translate id="homepage.benchmarks.flores.languages">English → 39 languages</Translate></li>
            <li><strong><Translate id="homepage.benchmarks.flores.entries">Entries:</Translate></strong> <Translate id="homepage.benchmarks.flores.entryCount">1,012 sentences per language</Translate></li>
            <li><strong><Translate id="homepage.benchmarks.flores.license">License:</Translate></strong> CC BY-SA 4.0</li>
            <li><strong><Translate id="homepage.benchmarks.flores.source">Source:</Translate></strong> OLDI / HuggingFace</li>
          </ul>
        </div>
      </div>
    </section>
  );
}

function LinksSection() {
  const links = [
    {label: translate({id: 'homepage.links.submit', message: 'Submit a Method'}), to: '/docs/getting-started/submit-a-method'},
    {label: translate({id: 'homepage.links.sovereignty', message: 'Data Sovereignty'}), to: '/docs/sovereignty/data-sovereignty'},
    {label: translate({id: 'homepage.links.economic', message: 'Economic Model'}), to: '/docs/sovereignty/economic-model'},
    {label: translate({id: 'homepage.links.communities', message: 'For Language Communities'}), to: '/docs/community/for-language-communities'},
    {label: translate({id: 'homepage.links.leaderboard', message: 'Leaderboard'}), to: 'https://champollion.dev/leaderboard'},
    {label: translate({id: 'homepage.links.cli', message: 'champollion CLI'}), to: 'https://champollion.dev'},
  ];

  return (
    <section className={styles.links}>
      <h2 className={styles.sectionTitle}>
        <Translate id="homepage.links.title">Learn More</Translate>
      </h2>
      <div className={styles.linkGrid}>
        {links.map((link, idx) => (
          <a
            key={idx}
            href={link.to}
            className={styles.linkCard}
            target={link.to.startsWith('http') ? '_blank' : undefined}
            rel={link.to.startsWith('http') ? 'noopener noreferrer' : undefined}
          >
            {link.label} →
          </a>
        ))}
      </div>
    </section>
  );
}

export default function Home() {
  return (
    <Layout
      title={translate({id: 'homepage.layout.title', message: 'The MT Eval Arena'})}
      description={translate({
        id: 'homepage.layout.description',
        message: 'An open benchmarking platform for machine translation methods, with a focus on languages that commercial services will never support.',
      })}
    >
      <HeroSection />
      <main>
        <PitchSection />
        <CurrentBenchmarks />
        <LinksSection />
      </main>
    </Layout>
  );
}
