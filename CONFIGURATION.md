## Airflow configuration

Some DAGs will require a few
[variables](https://airflow.incubator.apache.org/concepts.html#variables) and
[connections](https://airflow.incubator.apache.org/configuration.html#connections)
to be configured in order to run properly. Below are listed all the variables
available throughout the code base together with their descriptions.

## Connections

| Connection name  | Type       | Description                   |
| ---------------  | ----       | -----------                   |
| `api_db`         | `postgres` | API database                  |
| `explorer_db`    | `postgres` | OpenTrials Explorer database  |
| `warehouse_db`   | `postgres` | OpenTrials Warehouse database |
| `datastore_http` | `http`     | URL of the S3 bucket to use   |
| `datastore_s3`   | `s3`       | URL of the S3 bucket to use   |


## Variables

### Sources variables

These are variables used by their respective sources' collectors and processors.
For example, `HRA_URL` is used by the `hra` collector.
In simpler terms, these are generally related to collecting data.

| Variable name          | Description                                                       |
| -------------          | -----------                                                       |
| `DOWNLOAD_DELAY`       | Requests rate limit for scraping                                  |
| `COCHRANE_ARCHIVE_URL` | Location of the [Cochrane](http://www.cochrane.org/) data archive |
| `HRA_ENV`              | [HRA](https://www.harp.org.uk) environment (e.g. `production`)    |
| `HRA_PASS`             | [HRA](https://www.harp.org.uk) password                           |
| `HRA_URL`              | [HRA](https://www.harp.org.uk) URL                                |
| `HRA_USER`             | [HRA](https://www.harp.org.uk) user name                          |
| `ICTRP_PASS`           | [ICTRP](http://www.who.int/ictrp/en/) password                    |
| `ICTRP_USER`           | [ICTRP](http://www.who.int/ictrp/en/) user name                   |

### Utilities

These variables are used for defining general system settings or running data processing tasks.

| Variable name            | Description                                                           |
| -------------            | ------------                                                          |
| `DOCKER_API_VERSION`     | [Docker API version to use](https://airflow.incubator.apache.org/_modules/airflow/operators/docker_operator.html) (for compatibility with **older** runtimes) |
| `ENV`                    | Python environment to be used                                         |
| `DOCUMENTCLOUD_PASSWORD` | DocumentCloud password                                                |
| `DOCUMENTCLOUD_PROJECT`  | DocumentCloud project identifier                                      |
| `DOCUMENTCLOUD_USERNAME` | DocumentCloud user name                                               |
| `AWS_ACCESS_KEY_ID`      | AWS access key ID                                                     |
| `AWS_SECRET_ACCESS_KEY`  | AWS access key                                                        |
| `AWS_S3_BUCKET`          | S3 bucket                                                             |
| `AWS_S3_REGION`          | S3 region                                                             |
| `AWS_S3_CUSTOM_DOMAIN`   | S3 custom domain to use when creating public URLs for stored files    |

### Logging and monitoring

The variables here relate to logging and error monitoring features of (some of) the DAGs.

| Variable name          | Description                                                   |
| -------------          | ------------                                                  |
| `LOGGING_URL`          | [Papertrail](https://papertrailapp.com/) endpoint for logging |
| `COLLECTOR_SENTRY_DSN` | [Sentry](https://sentry.io/) endpoint for Collectors          |
| `PROCESSOR_SENTRY_DSN` | [Sentry](https://sentry.io/) endpoint for Processors          |
