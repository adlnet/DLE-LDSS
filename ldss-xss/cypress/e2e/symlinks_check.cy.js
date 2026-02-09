describe('Forbidden file access', () => {
  const paths = [
    '/Passwords.txt',
    '/../../../../etc/passwd',
    '/static/../etc/passwd',
    '/media/../../../secret.txt',
  ];

  paths.forEach((p) => {
    it(`should 404 on GET ${p}`, () => {
      cy.request({
        url: p,
        failOnStatusCode: false,  // don’t error out on a 4xx/5xx
      }).then((resp) => {
        expect(resp.status).to.equal(404);
      });
    });
  });
});