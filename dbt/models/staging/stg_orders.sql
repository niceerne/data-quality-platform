with src as (
    select * from {{ source('raw', 'orders') }}
),
dedup as (
    select *, row_number() over (partition by order_id order by order_date) as rn
    from src
)
select
    order_id::int            as order_id,
    customer_id::int         as customer_id,
    amount::numeric(12, 2)   as amount,
    order_date::date         as order_date
from dedup
where rn = 1
  and customer_id is not null
  and amount >= 0
  and order_date::date <= current_date
