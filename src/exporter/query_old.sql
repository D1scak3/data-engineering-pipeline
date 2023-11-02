\copy (
    select json_agg(row_to_json(t)) :: text
    from (
         select rim_facts.id, prices.id, plans.id, prices.created_at, prices.updated_at, prices.value, prices.currency, plans.plan_type
         from rim_facts, prices, plans
         where rim_facts.plan_id = plans.id
         and rim_facts.price_id = prices.id
         ) t
) to '/tmp/json_data.json'