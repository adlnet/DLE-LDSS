/// <reference types="Cypress" />

describe('homepage', () => {
  beforeEach(() => {
      // Cypress starts out with a blank slate for each test
      // so we must tell it to visit our website with the `cy.visit()` command.
      // Since we want to visit the same URL at the start of all our tests,
      // we include it in our beforeEach function so that it runs before each test
      cy.visit('/')
  })

  // Test for standard encoding format for all HTML content https://sdelements.il2.dso.mil/bunits/platform1/ecc/openlxp-xds/tasks/phase/testing/395-T132/
  it('Check content-type headers', () => {
    cy.request('/').as('resp')
    cy.get('@resp').its('headers').its('content-type')
      .should('include', 'text/html; charset=utf-8')
  });
});

