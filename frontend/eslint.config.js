import js from '@eslint/js'
import reactPlugin from 'eslint-plugin-react'
import reactHooks from 'eslint-plugin-react-hooks'
import globals from 'globals'

export default [
  js.configs.recommended,
  {
    files: ['src/**/*.{js,jsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooks,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off', // not needed with React 17+
      'react/prop-types': 'off', // no TypeScript PropTypes enforcement
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    },
    settings: {
      react: { version: 'detect' },
    },
  },
  {
    files: ['src/__tests__/**/*.{js,jsx}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2022,
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        vi: 'readonly',
      },
    },
  },
]
