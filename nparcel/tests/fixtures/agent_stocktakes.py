[
    {
        'id': 1,
        'agent_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'TEST_REF_001',
    },
    {
        'id': 2,
        'agent_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'TEST_REF_NOT_PROC',
    },
    {
        'id': 3,
        'agent_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'TEST_REF_NOT_PROC_PCKD_UP',
    },
    {
        'id': 4,
        'agent_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'JOB_TEST_REF_NOT_PCKD_UP',
    },
    {
        'id': 5,
        'agent_id': 3,
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(8)),
        'reference_nbr': 'TEST_REF_OLD_DATE',
    },
    {
        'id': 6,
        'agent_id': 1,
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(8)),
        'reference_nbr': 'AGENT_COMPLIANCE',
    },
    {
        'id': 7,
        'agent_id': 1,
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(10)),
        'reference_nbr': 'AGENT_COMPLIANCE_OLDER',
    },
    {
        # Duplicate.
        'id': 8,
        'agent_id': 1,
        'created_ts': str(datetime.datetime.now() - datetime.timedelta(10)),
        'reference_nbr': 'AGENT_COMPLIANCE_OLDER',
    },
    {
        # In agent_stocktake but not in TPP.
        'id': 9,
        'agent_id': 4,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'banana_reference',
    },
    {
        # In agent_stocktake but not in TPP.
        'id': 10,
        'agent_id': 4,
        'created_ts': str(datetime.datetime.now()),
        'reference_nbr': 'agent_exception_ref',
    },
]
