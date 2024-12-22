WITH RECURSIVE
	transactions AS (
		SELECT
			-- Adjust the timestamp by subtracting the day_start_hour to make each "day" start at specified hour
			t.created - (INTERVAL '1 hour' * :day_start_hour$4) AS adjusted_ts,
			t.*
		FROM pos_transactions_rich t
		-- Adjust the date range by the day_start_hour offset
		WHERE t.created BETWEEN (:date_from$1::TIMESTAMP) - (INTERVAL '1 hour' * :day_start_hour$4)
			AND (:date_to$2::TIMESTAMP) - (INTERVAL '1 hour' * :day_start_hour$4)
	),
	time_slots AS (
		-- Generate base time slot aligned to granularity
		SELECT
			CASE
				-- For daily granularity, truncate to day
				WHEN :granularity_minutes$3 = 1440 THEN
					DATE_TRUNC('day', MIN(adjusted_ts)) - INTERVAL '8 days'
				ELSE
					DATE_TRUNC('hour', MIN(adjusted_ts)) - INTERVAL '8 hours' +
					(INTERVAL '1 minute' *
					 (EXTRACT(MINUTE FROM MIN(adjusted_ts))::INTEGER / :granularity_minutes$3 * :granularity_minutes$3)
						)
				END + (INTERVAL '1 hour' * :day_start_hour$4) AS slot_start
		FROM transactions

		UNION ALL

		SELECT
			CASE
				WHEN :granularity_minutes$3 = 1440 THEN
					slot_start + INTERVAL '1 day'
				ELSE
					slot_start + (INTERVAL '1 minute' * :granularity_minutes$3)
				END
		FROM time_slots
		WHERE slot_start < (
			SELECT
				CASE
					WHEN :granularity_minutes$3 = 1440 THEN
						DATE_TRUNC('day', MAX(adjusted_ts)) + INTERVAL '8 days'
					ELSE
						DATE_TRUNC('hour', MAX(adjusted_ts)) + INTERVAL '8 hours' +
						(INTERVAL '1 minute' *
						 ((EXTRACT(MINUTE FROM MAX(adjusted_ts))::INTEGER / :granularity_minutes$3 + 1) * :granularity_minutes$3)
							)
					END + (INTERVAL '1 hour' * :day_start_hour$4)
			FROM transactions
		)
	),
	granular_stats AS (
		SELECT
			-- Round down to the nearest time slot based on granularity
			CASE
				WHEN :granularity_minutes$3 = 1440 THEN
					DATE_TRUNC('day', adjusted_ts)
				ELSE
					DATE_TRUNC('hour', adjusted_ts) +
					(INTERVAL '1 minute' * (EXTRACT(MINUTE FROM adjusted_ts)::INTEGER / :granularity_minutes$3 * :granularity_minutes$3))
				END + (INTERVAL '1 hour' * :day_start_hour$4) AS slot_start,

			-- Transaction counts
			COUNT(*) AS transaction_count,
			SUM(t.amount) AS transaction_sum,

			-- Organizer revenue
			SUM(t.org_comm) AS org_comm,

			-- Regular Orders
			COUNT(CASE WHEN t.is_order AND NOT t.vip THEN 1 END) AS regular_order_count,
			SUM(CASE WHEN t.is_order AND NOT t.vip THEN t.amount ELSE 0 END) AS regular_order_amount,
			SUM(CASE WHEN t.is_order AND NOT t.vip THEN t.total_amount_without_vat ELSE 0 END) AS regular_order_amount_without_vat,
			--/-- Sales
			COUNT(CASE WHEN t.amount > 0 AND t.is_order AND NOT t.vip THEN 1 END) AS regular_sales_count,
			SUM(CASE WHEN t.amount > 0 AND t.is_order AND NOT t.vip THEN t.amount ELSE 0 END) AS regular_sales_amount,
			SUM(CASE WHEN t.amount > 0 AND t.is_order AND NOT t.vip THEN t.total_amount_without_vat ELSE 0 END) AS regular_sales_amount_without_vat,
			--/-- Refunds
			COUNT(CASE WHEN t.amount < 0 AND t.is_order AND NOT t.vip THEN 1 END) AS refund_count,
			SUM(CASE WHEN t.amount < 0 AND t.is_order AND NOT t.vip THEN t.amount ELSE 0 END) AS refund_amount,

			-- VIP Orders
			COUNT(CASE WHEN t.is_order AND t.vip THEN 1 END) AS vip_order_count,
			SUM(CASE WHEN t.is_order AND t.vip THEN t.amount ELSE 0 END) AS vip_order_amount,
			SUM(CASE WHEN t.is_order AND t.vip THEN t.total_amount_without_vat ELSE 0 END) AS vip_order_amount_without_vat,
			--/-- Sales
			COUNT(CASE WHEN t.amount > 0 AND t.is_order AND t.vip THEN 1 END) AS vip_sales_count,
			SUM(CASE WHEN t.amount > 0 AND t.is_order AND t.vip THEN t.amount ELSE 0 END) AS vip_sales_amount,
			SUM(CASE WHEN t.amount > 0 AND t.is_order AND t.vip THEN t.total_amount_without_vat ELSE 0 END) AS vip_sales_amount_without_vat,
			--/-- Refunds
			COUNT(CASE WHEN t.amount < 0 AND t.is_order AND t.vip THEN 1 END) AS vip_refund_count,
			SUM(CASE WHEN t.amount < 0 AND t.is_order AND t.vip THEN t.amount ELSE 0 END) AS vip_refund_amount,

			-- Regular Charge Top-ups
			COUNT(CASE WHEN t.amount > 0 AND NOT t.is_order AND NOT t.vip THEN 1 END) AS topup_count,
			SUM(CASE WHEN t.amount > 0 AND NOT t.is_order AND NOT t.vip THEN t.amount ELSE 0 END) AS topup_amount,
			-- VIP Charge Top-ups
			COUNT(CASE WHEN t.amount > 0 AND NOT t.is_order AND t.vip THEN 1 END) AS vip_topup_count,
			SUM(CASE WHEN t.amount > 0 AND NOT t.is_order AND t.vip THEN t.amount ELSE 0 END) AS vip_topup_amount
		FROM transactions t
		GROUP BY slot_start
	)
SELECT
	ts.slot_start,
	-- Stats
	COALESCE(gs.transaction_count, 0) AS transaction_count,
	COALESCE(gs.transaction_sum, 0) AS transaction_sum,
	COALESCE(gs.org_comm, 0) AS org_comm,
	COALESCE(gs.regular_order_count, 0) AS regular_order_count,
	COALESCE(gs.regular_order_amount, 0) AS regular_order_amount,
	COALESCE(gs.regular_order_amount_without_vat, 0) AS regular_order_amount_without_vat,
	COALESCE(gs.regular_sales_count, 0) AS regular_sales_count,
	COALESCE(gs.regular_sales_amount, 0) AS regular_sales_amount,
	COALESCE(gs.regular_sales_amount_without_vat, 0) AS regular_sales_amount_without_vat,
	COALESCE(gs.refund_count, 0) AS refund_count,
	COALESCE(gs.refund_amount, 0) AS refund_amount,
	COALESCE(gs.vip_order_count, 0) AS vip_order_count,
	COALESCE(gs.vip_order_amount, 0) AS vip_order_amount,
	COALESCE(gs.vip_order_amount_without_vat, 0) AS vip_order_amount_without_vat,
	COALESCE(gs.vip_sales_count, 0) AS vip_sales_count,
	COALESCE(gs.vip_sales_amount, 0) AS vip_sales_amount,
	COALESCE(gs.vip_sales_amount_without_vat, 0) AS vip_sales_amount_without_vat,
	COALESCE(gs.vip_refund_count, 0) AS vip_refund_count,
	COALESCE(gs.vip_refund_amount, 0) AS vip_refund_amount,
	COALESCE(gs.topup_count, 0) AS topup_count,
	COALESCE(gs.topup_amount, 0) AS topup_amount,
	COALESCE(gs.vip_topup_count, 0) AS vip_topup_count,
	COALESCE(gs.vip_topup_amount, 0) AS vip_topup_amount
-- Cumulative stats
-- 	SUM(gs.regular_order_amount + vip_order_amount) OVER (ORDER BY ts.slot_start) AS cumulative_orders,
-- 	SUM(gs.regular_order_amount_without_vat + vip_order_amount_without_vat) OVER (ORDER BY ts.slot_start) AS cumulative_sales_without_vat,
-- 	SUM(gs.org_comm) OVER (ORDER BY ts.slot_start) AS cumulative_org_comm,
FROM time_slots ts
	LEFT JOIN granular_stats gs ON ts.slot_start = gs.slot_start
ORDER BY ts.slot_start;