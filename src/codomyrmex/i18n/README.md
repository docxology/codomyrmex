# Internationalization Module

Translation, localization, and message bundle management.

```python
from codomyrmex.i18n import Translator, Locale, MessageBundle, t

translator = Translator()
bundle = MessageBundle(Locale("es"))
bundle.add("greeting", "Hola, {name}!")
translator.add_bundle(bundle)

translator.set_locale(Locale("es"))
print(translator.t("greeting", name="World"))  # "Hola, World!"
```

- [SPEC](SPEC.md) | [AGENTS](AGENTS.md) | [PAI](PAI.md)
