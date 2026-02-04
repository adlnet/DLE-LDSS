# LDSS Overview

LDSS is the user interface for the Learning Data Schema Service (LDSS), a system that manages metadata schemas, mappings, and vocabularies used to transform learning data between different schema representations.  
This UI provides administrators and developers with visual tools to explore, configure, and manage schema relationships across learning data systems.

The Experience Schema Service backend maintains referential representations of domain entities and their mappings—defining how to convert an entity from one schema representation to another.  
The LDSS UI exposes these capabilities through a responsive web interface built with **Next.js**, supporting efficient schema management and interoperability.

Features include:
- A web-based interface for managing object and record metadata schemas
- Tools for defining and visualizing schema mappings between source and target representations
- Vocabulary storage and linking to support semantic consistency across schemas
- Integration with a Django-based backend service
- Authentication and role-based access control using JWT
- A Docker image for containerized deployment
- Configurable API endpoints and environment variables for different deployments

### How to use LDSS?

LDSS can be deployed via Docker or integrated within a larger LDSS environment.  
Users with appropriate credentials can sign in using JWT authentication to access UI functionality based on their role (e.g., administrator, viewer, or editor).

Once authenticated, users can:
- View and edit stored metadata schemas
- Define transformation mappings between schemas
- Manage vocabulary links and relationships
- Interact with the underlying LDSS API through the integrated UI

See [Getting Started](startup.md) for installation instructions.
