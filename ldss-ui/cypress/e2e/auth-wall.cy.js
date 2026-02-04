describe("Authentication Wall", () => {
  const publicRoutes = [
    "/",
  ];

  const protectedRoutes = [
    "/table",
    "/search",
  ];

  function visitWithJWT(route, token) {
    cy.visit(route, {
      onBeforeLoad(win) {
        if (token) {
          // Set the Authorization header for fetch/XHR
          cy.stub(win, "fetch").callsFake((...args) => {
            const [url, options = {}] = args;
            const opts = {
              ...options,
              headers: {
                ...(options.headers || {}),
                Authorization: `Bearer ${token}`,
              },
            };
            return fetch(url, opts);
          });
        }
      },
    });
  }

  it("should allow public pages without authentication", () => {
    publicRoutes.forEach((route) => {
      cy.visit(route);
      cy.contains("body", /./); // Page should load some content
    });
  });

  it("should block protected pages without authentication", () => {
    protectedRoutes.forEach((route) => {
      cy.request({
        url: route,
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.be.oneOf([302, 401, 403, 404]);
      });
    });
  });

  it("should block protected pages with a bad JWT", () => {
    protectedRoutes.forEach((route) => {
      cy.request({
        url: route,
        failOnStatusCode: false,
        headers: {
          Authorization: `Bearer ${Cypress.env("badJWT")}`,
        },
      }).then((res) => {
        expect(res.status).to.be.oneOf([401, 403, 404]);
      });
    });
  });

  // TODO: 
  // Below tests don't work, since it seems like cypress needs to store tokens in localstorage
  // Doing that in test is fine, but in prod we're depending only on the Istio headers
  // Retest when we learn a better technique or the architecture changes (e.g. we adopt cookies)

  // it("should allow protected pages with a good JWT", () => {
  //   // Set JWT in localStorage before visiting
  //   cy.window().then((win) => {
  //     win.localStorage.setItem("token", Cypress.env("goodJWT"));
  //   });

  //   // Visit the page normally
  //   cy.visit("/table");

  //   // Assert that something unique to the /table page is visible
  //   cy.contains("Expected text on table page").should("be.visible");
  // });

  // it("allows access with good JWT", () => {
  //   cy.request({
  //     url: "/table",
  //     headers: {
  //       Authorization: `Bearer ${Cypress.env("GOOD_JWT")}`
  //     }
  //   }).then((res) => {
  //     expect(res.status).to.eq(200);
  //     expect(res.body).to.include("Expected text on table page");
  //   });
  // });

  // it("blocks access with bad JWT", () => {
  //   cy.request({
  //     url: "/table",
  //     failOnStatusCode: false,
  //     headers: {
  //       Authorization: `Bearer ${Cypress.env("BAD_JWT")}`
  //     }
  //   }).then((res) => {
  //     expect(res.status).to.eq(307); // redirected to /unauthorized
  //   });
  // });
});