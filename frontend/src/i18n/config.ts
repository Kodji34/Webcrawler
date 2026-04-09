import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import enCommon from '../locales/en/common.json'
import frCommon from '../locales/fr/common.json'

export const languageStorageKey = 'pycrawler-language'

function detectLanguage() {
  if (typeof window === 'undefined') {
    return 'en'
  }

  return window.localStorage.getItem(languageStorageKey) === 'fr' ? 'fr' : 'en'
}

void i18n.use(initReactI18next).init({
  resources: {
    en: { translation: enCommon },
    fr: { translation: frCommon },
  },
  lng: detectLanguage(),
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
})

export default i18n
