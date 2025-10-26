{{ config(materialized='view') }}

-- Topp 10 arbetsgivare med flest annonser
SELECT
    employer__name AS employer_name,
    COUNT(*) AS total_ads
FROM {{ ref('job_ads_staging') }}
WHERE employer__name IS NOT NULL
GROUP BY employer__name
ORDER BY total_ads DESC
LIMIT 10
