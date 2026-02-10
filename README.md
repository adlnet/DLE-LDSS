# DLE-LDSS – Linked Data and Schema Service

The **DLE Linked Data and Schema Service (LDSS)** is an open-source service for managing, serving, and validating linked data schemas.  
This repository contains the **LDSS service source code** along with **Kubernetes manifests** for deploying it in cloud-native environments.

LDSS is designed to support schema-driven systems, data interoperability, and standards-based linked data workflows.

## Missing Components
This repo does rely on XIAs as well (eXperience Indexing Agents), but these had to remain private in order to protect the data plan of some organizations.

---

## Components
- [LDSS Manifests](./ldss-manifests/README.md) - K8 Base Deployment Resources Documentation
- [LDSS UI](./ldss-ui//README.md) - LDSS UI Documentation
- [LDSS XSS](./ldss-xss/README.md) - LDSS XSS Documentation
- [LDSS XMS](./ldss-xms/README.md) - LDSS XMS Documentation 


---

## Installing node packages
Because this was built for a PartyBus deployment, the following code must be run in the root directory before you can build some systems:
```
npm install
```
