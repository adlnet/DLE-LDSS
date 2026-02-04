import '@testing-library/jest-dom';
import 'isomorphic-fetch';

if (typeof window !== 'undefined') {
  require('@testing-library/jest-dom');

  const { mockAnimationsApi } = require('jsdom-testing-mocks');
  mockAnimationsApi();
}