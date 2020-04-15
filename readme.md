amti
====
A Mechanical Turk Interface (amti)

`amti` is a CLI for Mechanical Turk that emphasizes the
ability to quickly *iterate* on and run *reproducible* crowdsourcing
experiments.

Design and deploy HITs to Amazon Mechanical Turk in a way that:

  1. allows HIT definitions to be tracked in version control.
  2. can manage and generate batches of HITs from JSON data.
  3. stores the results from HITs in a structured format on disk or in
     the cloud.

To get started as a user, see [Installation](#installation) and
[Quickstart](#quickstart) below. To develop `amti` see
[Development Setup](#development-setup) and
[Contributing](#contributing).


Installation
------------
`amti` requires Python 3.6. To install `amti`, currently you should just
install from source:

    pip install git+https://github.com/allenai/amti#egg=amti

`amti` is now on the path of whatever environment you installed the
package into.

Additionally, you'll need to make sure that your environment is setup to
use Mechanical Turk through [`boto3`][boto3] as described in
[this tutorial][python-mturk-tutorial].

[boto3]: http://boto3.readthedocs.io/en/latest/reference/services/mturk.html
[python-mturk-tutorial]: https://blog.mturk.com/tutorial-a-beginners-guide-to-crowdsourcing-ml-training-data-with-python-and-mturk-d8df4bdf2977


Quickstart
----------
In this section, we'll walk through an example use case of `amti` to run
a batch of `HTMLQuestion` HITs on Mechanical Turk. If you'd like more
background information beforehand, feel free to jump to the
[Concepts](#concepts) section.

`amti` comes built-in with two examples, an `HTMLQuestion` and an
`ExternalQuestion`. The `HTMLQuestion` is a form written in HTML that
MTurk hosts for you. The `ExternalQuestion` provides an iframe to your
website that eventually posts back to an MTurk endpoint. Find these
examples in [examples directory][examples-directory].

We'll walk through the `HTMLQuestion` example. All requests are made to
the Mechanical Turk sandbox unless you pass the `--live` flag, so feel
free to run this example without worrying about posting to the live
site.

  1. Create your batch by running:

         amti create-batch examples/html-question/definition examples/html-question/data.jsonl .

     This command creates a batch directory using the definition in
     `example/html-question/definition` and data in
     `examples/html-question/data.jsonl`. It saves the batch directory
     into our current directory (`.`) and uploads HITs for it to MTurk.

     You can see that the batch has been created in the current
     directory by running `ls`.

  2. Now, check the status of your batch by running:

         amti status-batch batch-*

     Where `batch-*` just needs to match the path to the batch directory
     that was created.

  3. Find and fill out the example HITs on MTurk in the
     [worker sandbox][worker-sandbox]. You'll want to search for the
     HITs using your requester account's user name.

  4. View the status of your now completed HITs with:

         amti status-batch batch-*

  5. (optional) If you want to cancel all the HITs in the batch:

         amti expire-batch batch-*

  6. Since your batch is now ready for review, review it with:

         amti review-batch batch-*

  7. Once you've approved all of your HITs, you can save the results
     from the batch:

         amti save-batch batch-*

     If you go into the batch directory, you'll now notice that it has a
     new `results` subdirectory with the information on your HITs and
     assignments.

  8. Since you've saved your batch, dispose of it from the MTurk site
     using:

         amti delete-batch batch-*

     This action will delete the batch from MTurk so that it doesn't pop
     up when you examine your open HITs; however, it leaves your batch
     directory intact and unchanged.

  9. Lastly, you can extract data from all the assignments you've saved
     into your batch directory using any of the `extract` commands. To
     view the available extraction formats, pass the `--help` option:

         $ amti extract --help
         Usage: amti extract [OPTIONS] COMMAND [ARGS]...

           Extract data from a batch to various formats.

           See the subcommands for extracting batch data into a specific format.

         Options:
           -h, --help  Show this message and exit.

         Commands:
           tabular  Extract data from BATCH_DIR to OUTPUT_PATH in a tabular format.
           xml      Extract XML data from assignments in BATCH_DIR to OUTPUT_DIR.

     The `tabular` command will extract the batch's data into an easy to
     work with tabular format:

         amti extract tabular batch-* batch-data.jsonl

     For real workflows, it would be a good idea to use the batch id in
     the name of the output file.

Now you've run a small HIT and have the results in a reproducible
format. It's easy to tar up and upload the batch directory to the cloud
where you can store information from many such HITs.

When developing your own `HTMLQuestion` HITs, you may want to preview
them locally before uploading to Mechanical Turk, with the
`preview-batch` command:

    amti preview-batch /path/to/definition/directory /path/to/data/file


[examples-directory]: ./examples/
[worker-sandbox]: https://workersandbox.mturk.com/


Overview
--------
`amti` may be used both as a command line interface for working with
Mechanical Turk as well as a library for scripting on top of Mechanical
Turk.

First, we'll discuss the major [Concepts](#concepts) you'll want to know
when working with `amti`, then we'll describe the
[CLI](#command-line-interface), and lastly we'll talk about using `amti`
as a [library](#library).

### Concepts

#### Mechanical Turk Concepts

The following are the major Mechanical Turk concepts. Most concepts
correspond to a resource endpoint in
[their ReSTful API][mturk-api]. We've linked each concept to the
relevant endpoint's documentation, where available:

  - [**HIT**][hit-doc]: A HIT (Human Intelligence Task) corresponds to a
    task that a Turker can perform. Usually, a HIT ends up being an HTML
    form that the Turker can submit. An example HIT could be "enter
    three tags for this image", where an image is also displayed on a
    web page. **Note** that a HIT is a specific task, not a kind of
    task. So, image labeling is not a HIT; but rather, labeling a
    specific image would be a HIT.
  - **HIT Type**: Because many HITs will be similar, there's a notion of
    HIT Type which describes a group of HITs. In particular, HIT Types
    have descriptions of the task, define a reward amount, title for the
    task, and other properties that are generally shared across multiple
    HITs.
  - [**Assignment**][assignment-doc]: Often it's desirable to have a HIT
    completed multiple times by different people. An assignment is a
    single opportunity to complete a HIT, and a crowdworker can't take
    multiple assignments for one HIT. So, an image that should be
    labeled by 3 people would be posted as one HIT with 3 assignments.

[mturk-api]: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/Welcome.html
[hit-doc]: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_HITDataStructureArticle.html
[assignment-doc]: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_AssignmentDataStructureArticle.html

#### `amti` Concepts

Mechanical Turk has some features that support creating batches of HITs;
however, they're not particularly well developed and aren't modeled by
the API. `amti`'s key concept is that of a *batch*. A *batch* is a
collection of HITs generated from some data using a template.

`amti` represents batches as directories with the following structure:

    batch-$BATCHID : root directory for the batch
    |- README : a text file for developers about the batch
    |- COMMIT : the commit SHA for the code that generated the batch
    |- BATCHID : a random UUID for the batch
    |- definition : files defining the HIT / HIT Type
    |  |- NOTES : any notes for developers that go along with the task
    |  |- question.xml.j2 : a jinja2 template for the HITs' question
    |  |- hittypeproperties.json : properties for the HIT Type
    |  |- hitproperties.json : properties for the HIT
    |- data.jsonl : data used to generate each HIT in the batch
    |- results : results from the HITs on the MTurk site
    |  |- hit-$ID : results for a single HIT from the batch
    |  |  |- hit.jsonl : data about the HIT from the MTurk site
    |  |  |- assignments.jsonl : results from the assignments
    |  |- ...

To create a batch, write a batch definition (see the
[example batch definition][example-batch-definition]), create some data
in the [JSON Lines][json-lines] format, and then create the batch using
`amti create-batch`. Use the `-h` option for details. You can find some
example data in the [`data.jsonl`][data-jsonl] file.

To check on the batch's status, use `amti status-batch`. Once the batch
has been fully worked by Turkers, you can manually review their work
with `amti review-batch`. After approving or rejecting all the HITs in
the batch, you can save the batch to disk with `amti
save-batch`. Finally, after saving the batch, you can delete all of its
HITs with `amti delete-batch`. Again, use `-h` for details.

[example-batch-definition]: ./examples/html-question/definition
[json-lines]: http://jsonlines.org/
[data-jsonl]: ./examples/html-question/data.jsonl

### Command Line Interface

To use `amti` as a CLI for Mechanical Turk, [install](#installation)
`amti` and then call it by typing `amti` at the command line:

    $ amti --help
    Usage: amti [OPTIONS] COMMAND [ARGS]...

      A Mechanical Turk Interface: a CLI for MTurk.

    Options:
      -v, --verbose  Set log level to DEBUG.
      -h, --help     Show this message and exit.

    Commands:
      associate-qual            Associate workers with a qualification.
      block-workers             Block workers by WorkerId.
      create-batch              Create a batch of HITs using DEFINITION_DIR and...
      create-qualificationtype  Create a Qualification Type using...
      delete-batch              Delete the batch of HITs defined in BATCH_DIR.
      disassociate-qual         Disassociate workers with a qualification.
      expire-batch              Expire all the HITs defined in BATCH_DIR.
      extract                   Extract data from a batch to various formats.
      notify-workers            Send notification message to workers.
      preview-batch             Preview a batch of rendered HITs using...
      review-batch              Review the batch of HITs defined in BATCH_DIR.
      save-batch                Save results from the batch of HITs defined in...
      status-batch              View the status of the batch of HITs defined in...
      unblock-workers           Unblock workers by WorkerId.

The CLI is self-documenting and hierarchical, so you should be able to
find anything you might need by starting from the top and using the `-h`
option.

### Library

To use `amti` as a library, pay attention to the two main subpackages:

  - [`amti/actions`][amti-actions]: Functions implementing all the
    actions used by `amti`.
  - [`amti/clis`][amti-clis]: CLIs for many of the actions used by
    `amti`. All CLI components are implemented using [`click`][click]
    and so can be reused in other applications.

[amti-actions]: ./amti/actions/
[amti-clis]: ./amti/clis/
[click]: http://click.pocoo.org/5/


Development Setup
-----------------
This setup guide assumes you have [`pyenv`][pyenv],
[`pyenv-virtualenv`][pyenv-virtualenv], and [`direnv`][direnv] installed
on your machine.

From the root of this repo, create a python environment for `amti` and
install the dependencies:

    pyenv install 3.6.4
    pyenv virtualenv 3.6.4 amti
    echo 'amti' > .python-version
    pip install -r requirements.txt

Then, make sure that you have the proper
[AWS environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html)
set in your `.envrc` file for this repo. In particular, you should have values
for either:

    AWS_ACCESS_KEY_ID
    AWS_SECRET_KEY
    AWS_SECRET_ACCESS_KEY

or

    AWS_PROFILE

That correspond to your Mechanical Turk account.

[pyenv]: https://github.com/pyenv/pyenv
[pyenv-virtualenv]: https://github.com/pyenv/pyenv-virtualenv
[direnv]: https://direnv.net/


Contributing
------------
`amti` is licensed under [Apache 2.0][apache2-license]. Feel free to
fork the project or do whatever you like under the terms of that
license.

For inquiries about the project, please file a GitHub issue. If you find
a bug or error in the code, pull requests are strongly preferred.

[apache2-license]: https://www.apache.org/licenses/LICENSE-2.0
