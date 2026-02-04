describe('Search Page Null Byte Input', () => {
  it('should reject search input containing a null byte', () => {
    cy.request({
      url: '/search?keyword=test%00injection',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property('error', 'Invalid keyword');
    });
  });
});