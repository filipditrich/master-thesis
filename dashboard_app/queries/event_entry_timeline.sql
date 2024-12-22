SELECT
	e.name_pub AS entry_name,
	s.name_pub AS stage_name,
	e.date_from AS start_time,
	e.date_to AS end_time
FROM event.entry e
	JOIN event.stage s ON e.stage_id = s.stage_id
-- only entries with main performer or band
WHERE EXISTS
(
	SELECT 1
	FROM event.entry_performer ep
	WHERE ep.entry_id = e.entry_id AND ep.main
)
	 OR EXISTS
	    (
		    SELECT 1
		    FROM event.entry_band eb
		    WHERE eb.entry_id = e.entry_id AND eb.main
	    )
	AND e.date_from BETWEEN :date_from$1 AND :date_to$2
UNION ALL
(
	SELECT
		'Day 1',
		NULL,
		'2024-07-04 06:00:00',
		'2024-07-05 06:00:00'
)
UNION ALL
(
	SELECT
		'Day 2',
		NULL,
		'2024-07-05 06:00:00',
		'2024-07-06 06:00:00'
)
UNION ALL
(
	SELECT
		'Day 3',
		NULL,
		'2024-07-06 06:00:00',
		'2024-07-07 06:00:00'
)
ORDER BY start_time