# kermes
A monorepo for the Kermes family of microservices

## Testing Locally

### Starting Localstack

Kermes uses `localstack` to emulate a functioning AWS in development.

```
$ localstack start
```

_Note that localstack requires a running Docker Daemon._

### Provisioning

When the localstack instance stops, all state is lost, including all of the required Kermes infrastructure. We need to re-provision everything.

```
$ cd provisioning
$ terraform apply -auto-approve
```

### Dev environment housekeeping

Now that we've got our infrastructure set up, we'll need to do some basic housekeeping. Most of the Kermes services require a user, so we need to create one. There is a json file in the repo with valid Dynamo JSON in it, so we'll use that:

```
$ awslocal dynamodb put-item --table-name "users" --item file://test-user.json
```

Now that we've got a user in place, we'll also need to verify our send-from email address for the delivery service:

```
$ awslocal ses verify-email-identity --email-address no-reply@kermes.dev
```

### Running services in a debugger

Until we've got a proper container orchestration solution in place, testing the system is a very manual process. We have to bring up each project locally, run it in debug mode, and send SQS messages from the command line. To do that, open the project's directory and make sure poetry creates a virtual environment:

```
$ cd fetcher
$ poetry install
$ poetry shell
$ code .
```

Note the name of the venv that Poetry creates. In Visual Studio Code, make sure you select the python interpreter embedded in that venv.

### To create a fetch message:

```
$ awslocal sqs send-message --queue-url=http://localhost:4566/000000000000/kermes-fetch-article.fifo --message-body "{\"user_id\":\"test-user\", \"url\":\"https://www.massive.se/blog/games-technology/ethical-worldbuilding-in-games/\", \"queue_date\": 1600735044.202102}" --message-group-id="1"
```

This command uses the test user created earlier. The `fetcher` service will pull down the article, write metadata to the `articles` table and write article content (and related images) to local S3. Due to the design of the system, an article fetch does not automatically result in a bind request, so you'll need to trigger a bind manually.

### To create a bind message:

```
$ awslocal sqs send-message --queue-url=http://localhost:4566/000000000000/kermes-bind-ebook.fifo --message-body "{\"user_id\":\"test-user\", \"queue_date\": 1600735044.202102}" --message-group-id="kermes"
```

This command uses the test user created earlier. The `binder` service will fetch all articles for the test user from the `articles` table, create and write an ePub-format ebook to S3, and write the ebook metadata to the `ebooks` table.

If the test user is set up to prefer Kindle delivery, the `binder` service will then write a message to the converter service queue, requesting a conversion to MOBI format. If not, the `binder` will write a message to the postmaster service queue, requesting delivery of the ebook.

### Converting an ebook

There's no sample command for this service, but the `converter` service does require that Calibre's CLI utilities be installed locally to handle ebook conversion. If you're on a Mac, these are part of the Calibre bundle, and the service assumes they're on the PATH.

### Delivering an ebook

There's no sample command for this service. The `postmaster` service uses local SES, which _does not actually send emails_. If you need to test actual email send functionality, you need to use _real SES_, which should be possible, as the service provides all necessary data. Upon a "successful" email delivery, the `postmaster` service will write a message to the clean up queue, so that the articles and related S3 files can be deleted to save space.

### Cleaning up after delivery

There's no sample command for this service. The `housekeeper` service will permanently delete articles and S3 content. It _does not_ delete the ebook (for now; I'm not sure how we'll handle this yet).
