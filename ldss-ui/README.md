<!-- ![SQL LRS Logo](doc/images/doc_logo.png) -->

# LDSS UI

[![CI](https://github.com/yetanalytics/lrsql/actions/workflows/test.yml/badge.svg)](https://code.il2.dso.mil/adl-ousd/LDSS/ldss-ui/-/pipelines)
[![CD](https://github.com/yetanalytics/lrsql/actions/workflows/build.yml/badge.svg)](https://code.il2.dso.mil/adl-ousd/LDSS/ldss-ui/-/pipelines)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-5e0b73.svg)](CODE_OF_CONDUCT.md)

A metadata and schema management service for learning record interoperability.

## What is the LDSS?

This is the UI for the Experience Schema Service. 

The Experience Schema Service maintains referential representations of domain entities, as well as transformational mappings that describe how to convert an entity from one particular schema representation to another.
This component responsible for managing pertinent object/record metadata schemas, and the mappings for transforming records from a source metadata schema to a target metadata schema. This component will also be used to store and link vocabularies from stored schema.

## Environment Variables

`CCV_BASE_URL` - This the instance of the XSS that you want the UI to query. ex: https://ccv.ldss.tla.adlnet.gov

`NODE_ENV` - `production`, `test`, `development`

## Deloitte Questions

### 1. What functionality is hooked up to backend APIs?
  - Getting Term Mapping Data
  - Getting XIA course catalogs
  - ... more to come monday
### 2. What functionality is not hooked up to backend APIs?
  - CSV Upload
  - Language Set Creation

### 3. What’s the error handling strategy when the backend APIs are down? I see some of them fallback to local JSON, anything else we need to know about?
### 4. I noticed the app uses Next.js with App Router, server-side rendering, implements CSP directly in the middleware file (not in next.config.js), and uses the native fetch API instead of axios or react query. Can you confirm if that's correct?
### 5. I see the form-data package is pinned to version 4.0.4 via resolutions. Is this because a P1 issue flagged it, or is there another reason for locking and overriding it at that version?

## Releases

For releases and release notes, see the [Releases](#) page.

## Documentation

<!-- When you are updating this section, don't forget to also update doc/index.md -->

[LDSS UI Overview](doc/overview.md)

### FAQ

- [General Questions](doc/general_faq.md)
- [Troubleshooting](doc/troubleshooting.md)

### Basic Configuration

- [Getting Started](doc/startup.md)
