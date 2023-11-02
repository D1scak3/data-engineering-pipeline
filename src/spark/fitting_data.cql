SELECT product_id,
        updated_timestamp as timestamp, 
        brand, 
        model as product,
        country,
        company,
        subscription as offer_type,
        price
FROM zenprice_values 
WHERE product = "Galaxy A51 128GB" 
AND model = "samsung" 
AND company = "movistar" 
AND country = "CL"
-- updated_timestamp <= toTimestamp(now()) - 3y - 2m 
