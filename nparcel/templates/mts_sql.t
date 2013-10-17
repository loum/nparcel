SELECT ds.servprov_gid,
       sl.short_description "Source DC",
       dl.province_code "Dest State",
       fmssb.shipment_gid,
       fsb.shipment_start_time,
       (SELECT dobr.order_base_refnum_value
        FROM dim_order_base_refnum_v dobr,
             join_order_base_refnum_v jobr
        WHERE dobr.order_base_refnum_dim_id = jobr.order_base_refnum_dim_id
        AND jobr.order_base_gid = fmssb.order_base_gid
        AND dobr.order_base_refnum_qual_gid ='TOLL.CON_NOTE') "Con Note",
        dt.fiscal_week,
        dt.week_ending,
        CASE to_char(fssb.PLANNED_ARRIVAL_LOCAL,'DD/MM/YYYY')
             WHEN '01/01/1800' then null
             ELSE planned_arrival_local
             END "Planned Arrival",
        CASE to_char(ACTUAL_ARRIVAL_LOCAL,'DD/MM/YYYY')
             WHEN '01/01/1800' then null
             ELSE actual_arrival_local
             END "Actual Arrival"                                
FROM fact_mts_shipment_su_bs_v fmssb,
     dim_bill_to_v dbt,
     dim_servprov_v ds,
     fact_shipment_buyside_v fsb,
     dim_location_v sl,
     dim_location_v dl,
     dim_time_v dt,
     fact_shipment_stop_buyside_v fssb,
     join_fact_shipment_buyside_v jfsb,
     dim_shipment_status_buyside_v dssb
WHERE fmssb.bill_to_id = dbt.bill_to_id
AND fmssb.servprov_id = ds.servprov_id
AND fmssb.or_source_location_id=sl.location_id
AND fmssb.or_dest_location_id = dl.location_id
AND fmssb.shipment_gid = fssb.shipment_gid
AND fmssb.drop_stop_num = fssb.stop_num
AND fmssb.shipment_gid = jfsb.shipment_gid
AND jfsb.status_id = dssb.status_id
AND fsb.shipment_start_date_id = dt.date_id
AND fmssb.shipment_gid = fsb.shipment_gid
AND (fsb.shipment_start_time between to_date('$from_date', 'DD/MM/YYYY')
     AND to_date('$to_date', 'DD/MM/YYYY'))
AND dbt.long_description = 'TOLL/CUST/GRAYSONLINE.GRAYSONLINE'
AND dssb.status_type_gid = 'FINANCIAL_S'
AND dssb.status_value_gid <> 'FINS_EXEMPT'
GROUP BY ds.servprov_gid,
         sl.short_description,
         dl.province_code,
         dl.short_description,
         fmssb.shipment_gid,
         fsb.shipment_start_time,
         fsb.shipment_end_time,
         dt.fiscal_week,
         dt.week_ending,
         fssb.stop_num,
         fssb.stop_activity,
         order_base_gid,
         fssb.planned_arrival_local,
         fssb.actual_arrival_local,
         dssb.status_type_gid,
         dssb.status_value_gid     
ORDER BY servprov_gid, fiscal_week
