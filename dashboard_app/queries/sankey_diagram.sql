WITH summary AS (
	SELECT
		SUM(CASE WHEN NOT t.is_order AND t.amount > 0 THEN t.amount ELSE 0 END) AS total_topup_amount,
		SUM(CASE WHEN NOT t.is_order AND t.amount > 0 AND t.payment_method_id = 9 THEN t.amount ELSE 0 END) AS online_topup_amount,
		SUM(CASE WHEN NOT t.is_order AND t.amount > 0 AND t.payment_method_id = 5 THEN t.amount ELSE 0 END) AS card_topup_amount,
		SUM(CASE WHEN NOT t.is_order AND t.amount > 0 AND t.payment_method_id = 6 THEN t.amount ELSE 0 END) AS cash_topup_amount,
		SUM(CASE WHEN NOT t.is_order AND t.amount > 0 AND t.payment_method_id = 8 THEN t.amount ELSE 0 END) AS vip_topup_amount,
		SUM(CASE WHEN t.is_order THEN t.amount ELSE 0 END) AS total_order_amount,
		SUM(CASE WHEN t.is_order AND NOT t.vip THEN t.amount ELSE 0 END) AS total_regular_order_amount,
		SUM(CASE WHEN t.is_order AND t.vip THEN t.amount ELSE 0 END) AS total_vip_order_amount,
		SUM(CASE WHEN t.is_order AND t.amount > 0 THEN t.amount ELSE 0 END) AS total_sales_amount,
		SUM(t.org_comm) AS organizer_commission,
		SUM(CASE WHEN t.is_order AND t.payment_method_id = 5 THEN t.amount ELSE 0 END) AS total_card_sales,
		SUM(CASE WHEN t.is_order AND t.payment_method_id = 6 THEN t.amount ELSE 0 END) AS total_cash_sales

	FROM pos_transactions_rich t
	WHERE t.created BETWEEN :date_from$1 AND :date_to$2
),
	orders_summary AS (
		SELECT
			SUM(t.total_amount) AS total_order_amount,
			-- external vendors sales
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' THEN t.total_amount ELSE 0 END) AS external_vendor_sales,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' THEN t.org_comm ELSE 0 END) AS external_vendor_commission,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 1 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_non_alcoholic,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 2 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_beer,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 3 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_wine,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 4 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_spirits,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 5 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_salty,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 6 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_sweet,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id = 7 THEN t.total_amount ELSE 0 END) AS external_vendor_sales_complimentary,
			SUM(CASE WHEN t.legal_name != 'Yashica Events a.s.' AND t.product_category_id IS NULL THEN t.total_amount ELSE 0 END) AS external_vendor_sales_other,
			-- organizer vendor sales
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 1 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_non_alcoholic,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 2 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_beer,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 3 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_wine,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 4 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_spirits,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 5 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_salty,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 6 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_sweet,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id = 7 THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_complimentary,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id IS NULL AND t.chip_id IS NOT NULL THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_other,
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' AND t.product_category_id IS NULL AND t.chip_id IS NULL THEN t.total_amount ELSE 0 END) AS organizer_vendor_sales_ticket,
			-- FIXME: random expenses
			SUM(CASE WHEN t.legal_name = 'Yashica Events a.s.' THEN t.total_amount * 1.0 ELSE 0 END) AS organizer_vendor_expenses
		FROM pos_order_products_rich t
		WHERE t.created BETWEEN :date_from$1 AND :date_to$2
	),
	chip_balances AS (
		SELECT
			SUM(cb.actual_balance) AS total_unclaimed_balance,
			SUM(cb.last_pos_balance) AS total_unused_balance,
			SUM(cb.bank_refunded_amount) AS total_refunded_amount
		FROM get_chip_customers(:date_from$1, :date_to$2) cb
		WHERE cb.vip = FALSE
	)
SELECT
	-- top-ups
	s.online_topup_amount AS top_up_online,
	s.card_topup_amount AS top_up_card,
	s.cash_topup_amount AS top_up_cash,
	s.vip_topup_amount AS top_up_vip,
	s.total_topup_amount AS top_up_total,

	-- non-chip sales
	s.total_card_sales + s.total_cash_sales AS non_chip_total,
	s.total_card_sales AS non_chip_card,
	s.total_cash_sales AS non_chip_cash,

	-- total event finances
	(s.total_topup_amount + s.total_card_sales + s.total_cash_sales) AS event_finances,

	-- vendor sales
	(s.total_order_amount) AS vendor_sales,

	-- external vendor sales
	os.external_vendor_sales AS vendor_external_sales,
	os.external_vendor_sales_non_alcoholic AS vendor_external_sales_non_alcoholic,
	os.external_vendor_sales_beer AS vendor_external_sales_beer,
	os.external_vendor_sales_wine AS vendor_external_sales_wine,
	os.external_vendor_sales_spirits AS vendor_external_sales_spirits,
	os.external_vendor_sales_salty AS vendor_external_sales_salty,
	os.external_vendor_sales_sweet AS vendor_external_sales_sweet,
	os.external_vendor_sales_complimentary AS vendor_external_sales_complimentary,
	os.external_vendor_sales_other AS vendor_external_sales_other,
	s.organizer_commission AS vendor_external_commission,
	(os.external_vendor_sales - s.organizer_commission) AS vendor_external_payout,

	-- organizer vendor sales
	os.organizer_vendor_sales AS vendor_organizer_sales,
	os.organizer_vendor_sales_non_alcoholic AS vendor_organizer_sales_non_alcoholic,
	os.organizer_vendor_sales_beer AS vendor_organizer_sales_beer,
	os.organizer_vendor_sales_wine AS vendor_organizer_sales_wine,
	os.organizer_vendor_sales_spirits AS vendor_organizer_sales_spirits,
	os.organizer_vendor_sales_salty AS vendor_organizer_sales_salty,
	os.organizer_vendor_sales_sweet AS vendor_organizer_sales_sweet,
	os.organizer_vendor_sales_complimentary AS vendor_organizer_sales_complimentary,
	os.organizer_vendor_sales_other AS vendor_organizer_sales_other,
	os.organizer_vendor_sales_ticket AS vendor_organizer_sales_ticket,
	os.organizer_vendor_expenses AS vendor_organizer_expenses,

	-- credit refunds
	cb.total_unused_balance AS balance_unused,
	cb.total_refunded_amount AS balance_unused_refunded,
	cb.total_unclaimed_balance AS balance_unused_unclaimed,
	cb.total_unclaimed_balance AS balance_unused_unclaimed_organizer,

	-- revenue (vendor_external_commission + balance_unused_unclaimed_organizer + vendor_organizer_sales - vendor_organizer_expenses)
	s.organizer_commission + cb.total_unclaimed_balance + os.organizer_vendor_sales - os.organizer_vendor_expenses AS revenue
FROM summary s, chip_balances cb, orders_summary os;
