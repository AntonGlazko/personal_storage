-- DAU (daily active users) in January 1997
CREATE OR REPLACE VIEW 	period_of_time AS
					SELECT 		date_trunc('day', dd):: date order_date
					FROM 		generate_series
        							( '1997-01-01'::timestamp 
        							, current_date::timestamp
        							, '1 day'::interval) dd;

CREATE OR REPLACE FUNCTION DAU(year_n int, month_n int)
	RETURNS TABLE
		(
		order_date date,
		dau bigint
		)
	LANGUAGE plpgsql
AS
$$
BEGIN
	RETURN QUERY(
		SELECT 		l.order_date AS order_date,
		COUNT(DISTINCT r.customer_id) AS dau
		FROM 		period_of_time AS l
		LEFT JOIN 	orders AS r
		ON			l.order_date = r.order_date
		GROUP BY	l.order_date
		HAVING		(EXTRACT(YEAR FROM l.order_date) = year_n)
				AND (EXTRACT(MONTH FROM l.order_date) = month_n)
		ORDER BY	l.order_date
	);
END;
$$;

SELECT * FROM DAU(1997, 1);


-- ARPU monthly
SELECT		l.order_month AS order_month,
			(r.revenue_by_month / l.uniq_customers) AS arpu
FROM 		(
			SELECT 		TO_CHAR(order_date, 'YYYY-MM') AS order_month,
						COUNT(DISTINCT customer_id) AS uniq_customers
			FROM 		orders
			GROUP BY	order_month
			ORDER BY	order_month ASC
			) AS l
JOIN		(
			SELECT		TO_CHAR(l.order_date, 'YYYY-MM') AS order_month,
						SUM(r.order_amount) AS revenue_by_month
			FROM 		orders AS l
			LEFT JOIN	(
							SELECT 		order_id,
							SUM(unit_price * quantity) AS order_amount
							FROM 		order_details
							GROUP BY	order_id
						) AS r
			ON			l.order_id = r.order_id
			GROUP BY	order_month
			ORDER BY	order_month
			) AS r
ON			l.order_month = r.order_month;


-- average frequency between purchases
WITH get_median AS (
	SELECT		AVG(next_order_date - order_date) AS mean_action_freq
	FROM
	(	SELECT		customer_id,
					order_date,
					LEAD(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)
					AS next_order_date
		FROM		orders
	) AS sq
	GROUP BY	customer_id)
SELECT		PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY mean_action_freq) AS median
FROM		get_median