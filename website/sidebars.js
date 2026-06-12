/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  arenaSidebar: [
    'intro',
    'how-it-works',
    'how-this-site-is-translated',
    {
      type: 'category',
      label: 'Position Pieces',
      collapsed: false,
      items: [
        'perspectives/translation-is-not-revitalization',
        'perspectives/how-speakers-get-paid',
        'perspectives/from-benchmark-to-daily-use',
        'perspectives/reporting-errors-and-owning-corrections',
      ],
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/submit-a-method',
        'getting-started/agent-guide',
        'getting-started/contributing-compute',
        'getting-started/deploy-to-production',
        'getting-started/faq',
      ],
    },
    {
      type: 'category',
      label: 'Specifications',
      items: [
        'specifications/harness',
        'specifications/methods',
        'specifications/run-card',
        'specifications/scoring',
        'specifications/benchmark-spec',
      ],
    },
    {
      type: 'category',
      label: 'Leaderboard',
      items: [
        'leaderboard/rules',
        'leaderboard/datasets',
      ],
    },
    {
      type: 'category',
      label: 'Sovereignty',
      items: [
        'sovereignty/data-sovereignty',
        'sovereignty/ownership-transfer',
        'sovereignty/economic-model',
      ],
    },
    {
      type: 'category',
      label: 'Community',
      items: [
        'community/for-language-communities',
        'community/low-resource-languages',
      ],
    },
    {
      type: 'category',
      label: 'Context & History',
      items: [
        'context/history-of-language-and-computation',
        'context/what-counts-as-a-language',
      ],
    },
    {
      type: 'category',
      label: 'Tutorials & Cookbooks',
      items: [
        'tutorials/fst-gated-pipeline',
        'tutorials/coached-llm-prompting',
        'tutorials/few-shot-prompting',
        'tutorials/dictionary-augmented-llm',
        'tutorials/fine-tuned-model',
        'tutorials/chained-models',
        'tutorials/rule-based-hybrid',
        'tutorials/back-translation',
        'tutorials/evolutionary-approach',
        'tutorials/partial-translation',
        'tutorials/corpus-creation',
      ],
    },
  ],
};

export default sidebars;
