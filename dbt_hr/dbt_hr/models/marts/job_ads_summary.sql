
{{ config(materialized='view') }}

-- Summering av antal annonser per yrkesområde
SELECT
    occupation_field__label AS occupation_field,
    COUNT(*) AS job_count
FROM {{ ref('job_ads_staging') }}
GROUP BY occupation_field__label
ORDER BY job_count DESC
