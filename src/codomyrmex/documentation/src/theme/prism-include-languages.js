/**
 * Registration of extra Prism languages, swizzled from `@docusaurus/theme-classic`.
 *
 * Upstream resolves each configured language with
 * `require(`prismjs/components/prism-${lang}`)`. A template-literal `require`
 * makes webpack build a context module over every matching file, and nothing
 * tree-shakes it: the build shipped all 596 `prismjs/components/prism-*.js`
 * files inside `main.js`, whether or not any additional language was configured.
 * This site configures none (`themeConfig.prism` sets only `theme` and
 * `darkTheme`), so roughly 570 unused grammars were on the critical path of every
 * page load.
 *
 * This version keeps the behaviour — mount the instance on `globalThis`, register
 * the configured languages, restore the previous value — but loads the grammars
 * through a dynamic `import()`, which webpack emits as a lazy chunk instead of
 * part of the main bundle. With no `additionalLanguages` configured, nothing is
 * loaded at all.
 *
 * Upstream: `@docusaurus/theme-classic/lib/theme/prism-include-languages.js`.
 */
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import siteConfig from '@generated/docusaurus.config';

export default function prismIncludeLanguages(PrismObject) {
  if (!ExecutionEnvironment.canUseDOM) {
    return;
  }

  const {additionalLanguages = []} = siteConfig.themeConfig.prism ?? {};
  if (!additionalLanguages.length) {
    return;
  }

  // Prism components register themselves on the `Prism` instance found on the
  // global object, while prism-react-renderer uses its own instance. Mount ours
  // while the components load, then restore whatever was there before.
  const PrismBefore = globalThis.Prism;
  globalThis.Prism = PrismObject;

  const restorePrism = () => {
    delete globalThis.Prism;
    if (typeof PrismBefore !== 'undefined') {
      globalThis.Prism = PrismBefore;
    }
  };

  Promise.all(
    additionalLanguages.map((lang) =>
      lang === 'php'
        ? Promise.all([
            import('prismjs/components/prism-markup-templating.js'),
            import(`prismjs/components/prism-${lang}`),
          ])
        : import(`prismjs/components/prism-${lang}`),
    ),
  )
    .catch((error) => {
      // eslint-disable-next-line no-console
      console.error(
        'prism-include-languages: a configured Prism language failed to load',
        error,
      );
    })
    .finally(restorePrism);
}
