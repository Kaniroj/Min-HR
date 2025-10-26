
{{ config(materialized='view') }}

select *
from {{ source('staging', 'job_ads_resource') }}
