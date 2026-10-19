-- Nettoyage : dédoublonnage, typage, rejet des lignes invalides.
with src as (
    select * from {{ source('raw', 'customers') }}
),
dedup as (
    select *, row_number() over (partition by customer_id order by signup_date) as rn
    from src
)
select
    customer_id::int                  as customer_id,
    trim(name)                        as name,
    lower(trim(email))                as email,
    age::int                          as age,
    signup_date::date                 as signup_date
from dedup
where rn = 1
  and email ~ '^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$'
  and age between 0 and 120
  and signup_date::date <= current_date
  and name is not null
