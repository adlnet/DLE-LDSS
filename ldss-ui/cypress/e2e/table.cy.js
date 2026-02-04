// cypress/e2e/table.spec.js
describe('Table Component', () => {
    beforeEach(() => {
      // Stub the API call for contexts with options.
      cy.intercept('GET', '**/api/instances', {
        statusCode: 200,
        body: {
          coursera: { name: 'coursera', displayName: 'Coursera' },
          jko: { name: 'jko', displayName: 'Jko' },
          p2881: { name: 'p2881', displayName: 'P2881' },
          aetc: { name: 'aetc', displayName: 'Aetc' },
        },
      }).as('getContexts');
  
      // Default stub for the mapping API call. It returns one row using the query values.
      cy.intercept('GET', '**/api/mapped-terms*', (req) => {
        const source = req.query.source;
        const target = req.query.target || '';
        req.reply({
          statusCode: 200,
          body: [
            {
              source: { 
                alias: `Alias for ${req.query.source}`, 
                definition: `Definition for ${req.query.source}` },
              relationship: true,
              target: { 
                alias: `Alias for ${target}`, 
                definition: `Definition for ${target}` },
            },
          ],
        });
      }).as('getMappings');
  
      // Visit the page that renders the Table component.
      cy.visit('/table', {
        headers: { 'x-cypress-test': 'true' }
      });
      cy.wait('@getContexts');
    });
  
    it('renders the dropdowns and table structure', () => {
      // Ensure both dropdowns and the table are visible.
      cy.get('select#select-Source').should('be.visible')
      cy.get('select#select-Target').should('be.visible');
      cy.get('table').should('be.visible');
  
      // Initially, when no mappings are loaded, a "No mappings to display." message should appear.
      cy.contains('No mappings to display.').should('be.visible');
    });
  
    it('populates the dropdowns with the expected contexts', () => {
      cy.get('select#select-Source').should('exist').and('be.visible');

      cy.get('select#select-Source option').should('have.length', 5).then(options => {
        const filteredOptions = [...options].filter(option => option.value && option.value.trim() !== '');

        expect(filteredOptions).to.have.length(4);
        expect(filteredOptions[0].innerText.trim()).to.equal('Coursera');
        expect(filteredOptions[1].innerText.trim()).to.equal('Jko');
        expect(filteredOptions[2].innerText.trim()).to.equal('P2881');
        expect(filteredOptions[3].innerText.trim()).to.equal('Aetc');
      });
    });
  
    it('fetches and displays mappings when different dropdown options are selected', () => {
      // Select values
      cy.get('select#select-Source').select('Coursera');
      cy.get('select#select-Target').select('Jko');

      // Wait for mapping request
      cy.wait('@getMappings')
        .its('request.url')
        .should('include', 'source=coursera')
        .and('include', 'target=jko');

      // Wait for table to update
      cy.get('tbody tr').should('have.length', 1);

      cy.get('tbody tr').first().within(() => {
        cy.get('td').eq(0).should('contain', 'Alias for coursera');
        cy.get('td').eq(1).should('contain', 'Definition for coursera');
        cy.get('td').eq(2).should('contain', 'Equal');
        cy.get('td').eq(3).should('contain', 'Alias for jko');
        cy.get('td').eq(4).should('contain', 'Definition for jko');
      });
    });
  
    it('does not fetch mappings when the same context is selected for both source and target', () => {
      // Select the same option for both dropdowns.
      cy.get('select#select-Source').select('Coursera');
      cy.get('select#select-Target').select('Coursera');
  
      // Wait briefly to allow any (unexpected) mapping calls.
      cy.wait(500);
  
      // Assert that the mapping endpoint was never called.
      cy.get('@getMappings.all').should('have.length', 0);
  
      // The table should continue displaying the "No mappings to display." message.
      cy.contains('No mappings to display.').should('be.visible');
    });
  
    it('falls back to dummy data when the mapping API fails', () => {
      // Override the mapping API stub to simulate a failure.
      cy.intercept('GET', '**/api/mapped-terms*', {
        statusCode: 500,
        body: {},
      }).as('failMappings');
  
      // Select two different options to trigger the mapping fetch.
      cy.get('select#select-Source').select('Jko');
      cy.get('select#select-Target').select('P2881');
  
      // Wait for the failed mapping API call.
      cy.wait('@failMappings');
  
      // Since the mapping API fails, the component falls back to dummy data.
      // We don’t know the exact dummy data but we expect that the "No mappings to display." message is not shown.
      cy.get('tbody tr').should('not.contain', 'No mappings to display.');

      // Also, we expect at least one table row (from the dummy data) to be rendered.
      cy.get('tbody tr').its('length').should('be.greaterThan', 0);
    });
  });
  