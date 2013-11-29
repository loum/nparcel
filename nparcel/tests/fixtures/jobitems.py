[
    {
        'id': 1,
        'connote_nbr': '218501217863',
        'item_nbr': 'priority_item_nbr_001',
        'job_id': 1,
        'created_ts': str(datetime.datetime.now()),
        'pickup_ts': str(datetime.datetime.now()),
        'pod_name': 'pod_name 218501217863',
        'identity_type_id': 1,
        'identity_type_data': 'identity 218501217863',
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        'id': 2,
        'connote_nbr': '218501217old',
        'item_nbr': 'priority_item_nbr_old',
        'job_id': 1,
        'created_ts': str(datetime.datetime.now()),
        'notify_ts': str(datetime.datetime.now()),
        'pod_name': 'pod_name 218501217old',
        'identity_type_id': 1,
        'identity_type_data': 'identity 218501217old',
        'email_addr': 'loumar@tollgroup.com',
    },
    {
        'id': 3,
        'connote_nbr': 'pe_connote',
        'item_nbr': 'pe_item_nbr',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        'id': 4,
        'connote_nbr': 'pe_connote_02',
        'item_nbr': 'pe_item_nbr',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': '',
        'phone_nbr': ''
    },
    {
        'id': 5,
        'connote_nbr': 'pe_collected_connote',
        'item_nbr': 'pe_collected_connote',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'pickup_ts': str(datetime.datetime.now()),
        'pod_name': 'pod_name pe_collected',
        'identity_type_id': 1,
        'identity_type_data': 'identity pe_collected',
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        'id': 6,
        'connote_nbr': 'uncollected_connote_sc_1',
        'item_nbr': 'uncollected_connote_sc_1_item_nbr',
        'job_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        'id': 7,
        'connote_nbr': 'collected_connote_sc_1',
        'item_nbr': 'collected_sc_1_item_nbr',
        'job_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'pickup_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        'id': 8,
        'connote_nbr': 'uncoll_connote_sc_1_ntfy',
        'item_nbr': 'uncoll_sc_1_item_nbr_ntfy',
        'job_id': 3,
        'created_ts': str(datetime.datetime.now()),
        'notify_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Service Code 4 -- BU ID 2 (not exist in MTS or TransSend)
        'id': 9,
        'connote_nbr': 'uncollected_connote_sc_4',
        'item_nbr': 'uncollected_connote_sc_4_item_nbr',
        'job_id': 4,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Primary Elect -- delivered with recipients (MTS)
        'id': 10,
        'connote_nbr': 'GOLW010997',
        'item_nbr': 'GOLW010997',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Primary Elect -- delivered without recipients (MTS)
        'id': 11,
        'connote_nbr': 'GOLW012846',
        'item_nbr': 'GOLW012846',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': '',
        'phone_nbr': ''
    },
    {
        # Primary Elect -- delivered (TransSend)
        'id': 12,
        'connote_nbr': 'ANWD011307',
        'item_nbr': 'ANWD011307001',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Primary Elect -- not delivered (TransSend)
        'id': 13,
        'connote_nbr': 'IANZ012764',
        'item_nbr': 'IANZ012764',
        'job_id': 2,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Service Code 4 -- BU ID (1, ) delivered (TransSend)
        'id': 14,
        'connote_nbr': 'TWAD358893',
        'item_nbr': 'TWAD358893001',
        'job_id': 5,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Aged Parcel connote match.
        'id': 15,
        'connote_nbr': 'TEST_REF_001',
        'item_nbr': 'aged_connote_match',
        'job_id': 7,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Aged Parcel item_nbr match.
        'id': 16,
        'connote_nbr': 'aged_item_match',
        'item_nbr': 'TEST_REF_001',
        'job_id': 7,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
    {
        # Uncollected job_items -- bad recipients
        'id': 17,
        'connote_nbr': 'ARTZ061184',
        'item_nbr': '00393403250082030044',
        'job_id': 4,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': '.',
        'phone_nbr': ''
    },
    {
        # Uncollected job_items -- bad recipients
        'id': 18,
        'connote_nbr': 'ARTZ061184',
        'item_nbr': '00393403250082030045',
        'job_id': 4,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': '',
        'phone_nbr': '.'
    },
    {
        # Uncollected job_items -- matched via job.card_ref_nbr
        'id': 19,
        'connote_nbr': 'ARTZ061184',
        'item_nbr': '00393403250082030046',
        'job_id': 6,
        'created_ts': str(datetime.datetime.now()),
        'email_addr': 'loumar@tollgroup.com',
        'phone_nbr': '0431602145'
    },
]
