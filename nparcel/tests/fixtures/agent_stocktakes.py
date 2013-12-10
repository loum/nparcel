[
    {
        'id': 1,
        'agent_id': 'v999',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(50)),
        'reference_nbr': 'TEST_REF_001',
    },
    {
        'id': 2,
        'agent_id': 'v999',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(50)),
        'reference_nbr': 'TEST_REF_NOT_PROC',
    },
    {
        'id': 3,
        'agent_id': 'v999',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(50)),
        'reference_nbr': 'TEST_REF_NOT_PROC_PCKD_UP',
    },
    {
        'id': 4,
        'agent_id': 'v999',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(50)),
        'reference_nbr': 'JOB_TEST_REF_NOT_PROC_PCKD_UP',
    },
    {
        'id': 5,
        'agent_id': 'v999',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(8)),
        'reference_nbr': 'TEST_REF_OLD_DATE',
    },
    {
        'id': 6,
        'agent_id': 'N031',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(8)),
        'reference_nbr': 'AGENT_COMPLIANCE',
    },
    {
        'id': 7,
        'agent_id': 'N031',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(10)),
        'reference_nbr': 'AGENT_COMPLIANCE_OLDER',
    },
    {
        # Duplicate.
        'id': 8,
        'agent_id': 'N031',
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(10)),
        'reference_nbr': 'AGENT_COMPLIANCE_OLDER',
    },
]
