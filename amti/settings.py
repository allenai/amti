"""Constants and default settings that ship with ``amti``"""


# AWS client configuration

MAX_ATTEMPTS = 25
"""The number of retries to perform for requests."""


# Mechanical Turk environment values

ENVS = {
    'live': {
        'region_name': 'us-east-1',
        'endpoint_url': 'https://mturk-requester.us-east-1.amazonaws.com',
        'worker_url': 'https://www.mturk.com/',
        'requester_url': 'https://requester.mturk.com/'
    },
    'sandbox': {
        'region_name': 'us-east-1',
        'endpoint_url': 'https://mturk-requester-sandbox.us-east-1.amazonaws.com',
        'worker_url': 'https://workersandbox.mturk.com/',
        'requester_url': 'https://requestersandbox.mturk.com/'
    }
}


# batch directory structure and values

BATCH_README = """
This directory is a batch made by A Mechanical Turk Interface.

The files in this directory represent the definition for and potentially
the results of a batch of HITs on Amazon Mechanical Turk.

See the A Mechanical Turk Interface documentation for details.
"""

# a batch directory should have the following structure:
#
#    batch-$BATCHID : root directory for the batch
#    |- README : a text file for developers about the batch
#    |- COMMIT : the commit SHA for the code that generated the batch
#    |- BATCHID : a random UUID for the batch
#    |- definition : files defining the HIT / HIT Type
#    |  |- NOTES : any notes for developers that go along with the task
#    |  |- question.xml.j2 : a jinja2 template for the HITs' question
#    |  |- hittypeproperties.json : properties for the HIT Type
#    |  |- hitproperties.json : properties for the HIT
#    |- data.jsonl : data used to generate each HIT in the batch
#    |- results : results from the HITs on the MTurk site
#    |  |- hit-$ID : results for a single HIT from the batch
#    |  |  |- hit.jsonl : data about the HIT from the MTurk site
#    |  |  |- assignments.jsonl : results from the assignments
#    |  |- ...
#
# The following data structure maps a logical name for a structure (such
# as 'readme' for the 'README' file) to a pair giving the path name for
# that structure and the substructure of that structure (an empty
# dictionary if it's a file, or a similar structure if it's a
# directory).
#
# All directory structure should be captured here, so that it has a
# single source of truth.
BATCH_DIR_STRUCTURE = ('batch-{batch_id}', {
    'readme': ('README', {}),
    'commit': ('COMMIT', {}),
    'batchid': ('BATCHID', {}),
    'definition': ('definition', {
        'notes': ('NOTES', {}),
        'question_template': ('question.xml.j2', {}),
        'hittype_properties': ('hittypeproperties.json', {}),
        'hit_properties': ('hitproperties.json', {})
    }),
    'data': ('data.jsonl', {}),
    'results': ('results', {
        'hit_dir': ('hit-{hit_id}', {
            'hit': ('hit.jsonl', {}),
            'assignments': ('assignments.jsonl', {})
        })
    })
})

# the name of the file used to denote a batch which has been uploaded to
# MTurk but is not yet complete. This file also stores information
# relevant to completing the batch (i.e., the open HIT IDs and HIT Type
# ID).
INCOMPLETE_FILE_NAME = '_INCOMPLETE'

# template for the directories that contain the XML answers for an
# assignment
XML_DIR_NAME_TEMPLATE = 'batch-{batch_id}-xml'
# template for the files that contain the XML answers for an assignment
XML_FILE_NAME_TEMPLATE = 'assignment-{assignment_id}.xml'


HITTYPE_PROPERTIES = {
    'AutoApprovalDelayInSeconds': int,
    'AssignmentDurationInSeconds': int,
    'Reward': str,
    'Title': str,
    'Keywords': str,
    'Description': str
}

HIT_PROPERTIES = {
    'MaxAssignments': int,
    'LifetimeInSeconds': int
}


QUALIFICATIONTYPE_DIR_STRUCTURE = \
    ('qualification-type-{qualificationtype_id}', {
        'definition': ('definition', {
            'properties': ('qualificationtypeproperties.json', {}),
            'test': ('test.xml', {}),
            'answerkey': ('answerkey.xml', {})
        }),
        'qualificationtype': (
            'qualificationtype-{qualificationtype_id}.jsonl',
            {}
        )
    })


QUALIFICATIONTYPE_PROPERTIES = {
    'Name': str,
    'Keywords': str,
    'Description': str,
    'QualificationTypeStatus': str,
    'RetryDelayInSeconds': int,
    'TestDurationInSeconds': int
}
