select rim_facts.id as main_id, 
    prices.id as price_id, 
    plans.id as plan_id, 
    products.id as product_id, 
    -- prices.created_at, 
    prices.updated_at, 
    products.brand, 
    products.slug as model, 
    prices.value as price, 
    prices.currency, 
    organizations.country_code as country,
    organizations.name as company, 
    plans.plan_type
from rim_facts, prices, plans, products, organizations
where rim_facts.plan_id = plans.id
and rim_facts.price_id = prices.id
and rim_facts.product_id = products.id
and rim_facts.organization_id = organizations.id