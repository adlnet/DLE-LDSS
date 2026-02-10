# WELCOME TO YOUR NEW MANIFESTS

## Access

Your staging url is https://ldss.staging.dso.mil

## What is this?

This project is the source of truth for your application in staging/production.  It is instantiated as a bare bones guess at what your app needs to deploy.  It should serve to get your app 95% of the way there, with individual fixes needed for this specific app.

You should see a few folders

- base : k8s resources placed here are deployed to all environments you have set, e.g. il2 staging, il4 prod, etc.
- il4 : k8s resources placed here are specific to your il4 environments but would affect both staging and prod if it were set up.
- il4/overlays/staging : k8s resources placed here only affect il4 staging.
- If you have a MySQL database, these are the resources injected to mission-bootstrap project to instantiate your apps database. It will create a mysql database called ldss_db with the following users and passwords loaded to the respective env variable in the container that connects to the database:
  - MYSQL_HOST
  - MYSQL_PORT
  - MYSQL_DB_NAME
  - MYSQL_DB_ADMIN_USER (Pass Var: MYSQL_DB_ADMIN_PASSWORD)
  - MYSQL_DB_RW_USER    (Pass Var: MYSQL_DB_RW_PASSWORD)
  - MYSQL_DB_RO_USER    (Pass Var: MYSQL_DB_RO_PASSWORD)
- If you have minio, these are the resources injected to mission-bootstrap project to instantiate minio.
  - MINIO_BUCKET_NAME
  - MINIO_ACCESS_KEY
  - MINIO_SECRET_KEY
  - MINIO_ENDPOINT_URL
  - MINIO_REGION
  - MINIO_HOST
  - MINIO_PORT
  - MINIO_PROTOCOL
  - S3_BUCKET_UUID
## What's next?

If you haven't already, you need to make sure your application is passing the official P1 pipelines. CTF will needed for production, but you can get to staging and get an internet accessible url as long as you are passing pipeline tests. 

- With pipelines green, an infrastructure team member can add a deploy stage to the end of the pipeline to upload your release candidate image to the container registry on THIS project, and release images to the mission-bootstrap project's container registry.

The last step before deployment is to verify that pipelines can push generated images to respective container registry and that the pipeline automatically increments image tags on manifests.

At this point, if you have images built from your pipelines and your bootstrap integration & manifest repo is setup, your app should be live in staging! The default url is https://ldss.staging.dso.mil.

## Environment database values

| Environment variable | Value |
| --- | --- |
| MYSQL_DB_NAME   | ldss_db |
| MYSQL_DB_NAME_1 | ldss_xis_db |
| MYSQL_DB_NAME_2 | ldss_xds_db |
| MYSQL_DB_NAME_3 | ldss_xms_db |
| MYSQL_DB_NAME_4 | ldss_xia_aetc_db |
| MYSQL_DB_NAME_5 | ldss_xia_dau_db |
| MYSQL_DB_NAME_6 | ldss_xia_jko_db |
| MYSQL_DB_NAME_7 | ldss_xss_db |
| MYSQL_HOST | mission-mysql.admin.il2.dsop.io |

## How to manage

You are free to make changes to this repo. When a new change is committed, your app will automatically sync up with the changes. For more information on what is permitted, see [confluence article on permitted activites](https://confluence.il2.dso.mil/pages/viewpage.action?spaceKey=P1MDOHD&title=HowTo+-+Manifests+-+Permitted+Activities).
