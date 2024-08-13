with TermFinder as (
SELECT
	terms.id as tid,
	case
		when sysdate >= terms.firstday AND sysdate <= terms.lastday then 'Active'
		else 'Inactive'
	end as tstatus
FROM
	terms
WHERE
	terms.yearid = ~(curyearid)
	and terms.schoolid = 495 -- ~(curschoolid)
)

SELECT
	LISTAGG(tf.tid, ', ')
FROM
	TermFinder tf
WHERE
	tf.tstatus = 'Active'
