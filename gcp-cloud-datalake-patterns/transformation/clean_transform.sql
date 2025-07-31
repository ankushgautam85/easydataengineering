CREATE OR REPLACE TABLE my_dataset.cleaned_data AS
SELECT
    user_id,
    LOWER(email) AS normalized_email,
    PARSE_DATE('%Y-%m-%d', registration_date) AS reg_date,
    IF(is_active = 'yes', TRUE, FALSE) AS active_flag
FROM
    my_dataset.raw_data
WHERE
    registration_date IS NOT NULL;
