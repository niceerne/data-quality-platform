-- Suivi quotidien de la qualité par table et par contrôle.
select
    checked_at::date                                   as check_date,
    table_name,
    check_name,
    count(*)                                           as nb_checks,
    sum(case when status = 'FAIL' then 1 else 0 end)   as nb_failures,
    sum(failed_rows)                                   as failed_rows,
    round(avg(failure_rate)::numeric, 4)               as avg_failure_rate
from {{ source('dq', 'check_results') }}
group by 1, 2, 3
